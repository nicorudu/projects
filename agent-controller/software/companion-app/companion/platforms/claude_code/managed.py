"""Claude Code sessions the companion app starts itself (replaces the v0 main.py).

Runs `claude -p <task> --output-format stream-json --verbose` and turns the stream into
session status. Permissions are NOT skipped any more: if the hooks are installed, every
approval comes to the device like any other session; in -p mode a request nobody answers
is denied by Claude Code, so nothing runs unapproved.

Voice prompts (M2) will use this to start work from the controller.
"""

from __future__ import annotations

import asyncio
import json
import logging

from ...core.state import Status
from .attached import NAME, summarize

log = logging.getLogger(__name__)


async def run_task(app, task: str, cwd: str | None = None, claude_bin: str = "claude",
                   skip_permissions: bool = False) -> str | None:
    """Run one task to completion. Returns the session id (None if claude never started one)."""
    args = [claude_bin, "-p", task, "--output-format", "stream-json", "--verbose"]
    if skip_permissions:
        args.append("--dangerously-skip-permissions")
    proc = await asyncio.create_subprocess_exec(*args, cwd=cwd, stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.DEVNULL)
    sid = None
    assert proc.stdout
    async for raw in proc.stdout:
        line = raw.decode(errors="replace").strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = m.get("session_id") or sid
        if not sid:
            continue
        t = m.get("type")
        if t == "system" and m.get("subtype") == "init":
            app.upsert_session(NAME, sid, m.get("cwd") or cwd, status=Status.WORKING, text="> " + task[:300])
        elif t == "assistant":
            for block in m.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tool = block.get("name", "")
                    app.upsert_session(NAME, sid, status=Status.WORKING,
                                       tool=f"{tool}: {summarize(tool, block.get('input'))}"[:200])
                elif block.get("type") == "text" and block.get("text", "").strip():
                    app.upsert_session(NAME, sid, text=block["text"].strip()[:2000])
        elif t == "result":
            app.upsert_session(NAME, sid, status=Status.ERROR if m.get("is_error") else Status.DONE,
                               tool="", text=str(m.get("result", ""))[:2000] or None)
    await proc.wait()
    log.info("managed task finished (session %s, exit %s)", sid, proc.returncode)
    return sid
