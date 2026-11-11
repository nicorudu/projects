"""Tiny SessionStart command hook: forwards the event plus which terminal tab it's in.

Claude Code runs this when a session starts (SessionStart only supports command hooks).
It adds `_term` (terminal app, TTY, app bundle id) so "Send" on the device can bring that
exact tab to the front. It never fails loudly and never blocks Claude Code: any error is ignored.

    python -m companion.hooks.report --url http://127.0.0.1:8766/hooks/claude
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8766/hooks/claude"


def _tty_of_ancestors(max_levels: int = 5) -> str:
    """The terminal device of the nearest ancestor process that has one (macOS/Linux)."""
    if os.name == "nt":
        return ""
    pid = os.getppid()
    for _ in range(max_levels):
        try:
            out = subprocess.run(["ps", "-o", "ppid=,tty=", "-p", str(pid)], capture_output=True,
                                 text=True, timeout=1).stdout.split()
        except (OSError, subprocess.SubprocessError):
            return ""
        if len(out) < 2:
            return ""
        ppid, tty = out[0], out[1]
        if tty not in ("?", "??", "-") and re.fullmatch(r"[\w/]+", tty):
            return tty if tty.startswith("/dev/") else f"/dev/{tty}"
        pid = int(ppid)
        if pid <= 1:
            return ""
    return ""


def terminal_info() -> dict:
    env = os.environ
    return {k: v for k, v in {
        "term_program": env.get("TERM_PROGRAM", ""),
        "bundle_id": env.get("__CFBundleIdentifier", ""),  # macOS: the app that owns the terminal
        "tty": _tty_of_ancestors(),
        "iterm_session": env.get("ITERM_SESSION_ID", ""),
        "wt_session": env.get("WT_SESSION", ""),  # Windows Terminal
    }.items() if v}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    url = argv[argv.index("--url") + 1] if "--url" in argv else DEFAULT_URL
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        payload["_term"] = terminal_info()
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # localhost: never via a proxy
        opener.open(req, timeout=1.5).read()
    except Exception:
        pass  # companion app not running, or anything else: stay silent
    return 0


if __name__ == "__main__":
    sys.exit(main())
