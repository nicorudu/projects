"""The command every Claude Code hook runs. Forwards the hook event to the companion app.

    python -m companion.hooks.report [--wait] [--url http://127.0.0.1:8766/hooks/claude]

Why a command and not Claude Code's built-in `http` hook type: if the companion app
isn't running, an http hook prints "hook error: ECONNREFUSED" in Claude Code on every
event (seen on the Mac Mini, 2026-11-11). This script stays completely silent instead.

- Status events are installed as **async** hooks: Claude Code never waits for them.
  Each one carries `_ts` (when the hook fired) so the app can put late arrivals in order.
- `--wait` is for PermissionRequest: it waits for the app's answer and prints it for
  Claude Code. App not running, or anything else wrong → prints nothing → no decision →
  Claude Code shows its normal prompt.
- SessionStart also carries `_term` (terminal app, TTY, app bundle id) so "Send" on the
  device can bring that exact tab to the front.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8766/hooks/claude"
WAIT_TIMEOUT_S = 590  # just under the 600 s hook timeout written by install-hooks
SEND_TIMEOUT_S = 2


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


def main(argv: list[str] | None = None, stdin=None, stdout=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    url = argv[argv.index("--url") + 1] if "--url" in argv else DEFAULT_URL
    wait = "--wait" in argv
    try:
        payload = json.loads(stdin.read() or "{}")
        payload["_ts"] = time.time()
        if payload.get("hook_event_name") == "SessionStart":
            payload["_term"] = terminal_info()
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # localhost: never via a proxy
        with opener.open(req, timeout=WAIT_TIMEOUT_S if wait else SEND_TIMEOUT_S) as r:
            body = r.read()
        if wait:
            answer = json.loads(body or b"{}")
            if isinstance(answer, dict) and answer:
                stdout.write(json.dumps(answer))
                stdout.flush()
    except Exception:
        pass  # companion app not running, or anything else: stay silent, no decision
    return 0


if __name__ == "__main__":
    sys.exit(main())
