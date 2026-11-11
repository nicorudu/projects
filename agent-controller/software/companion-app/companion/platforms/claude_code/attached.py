"""Claude Code plug-in: your normal terminal sessions, through Claude Code hooks.

Status comes from hook events. Approvals come from the PermissionRequest hook: the hook
server holds Claude Code's HTTP request open while the Approval screen is up, and answers
when a key is pressed. No decision (device off, timeout, "Ask in terminal") means Claude Code
shows its normal prompt, so nothing ever gets stuck or silently approved.

Fields used are the documented ones (code.claude.com/docs/en/hooks, checked 2026-11-11):
session_id, cwd, hook_event_name, tool_name, tool_input, permission_suggestions, prompt,
notification_type, message, last_assistant_message, reason.
"""

from __future__ import annotations

import asyncio
import itertools
import json
import logging
import sys

from ...core.state import Approval, Choice, Status
from ..base import Cap

log = logging.getLogger(__name__)

NAME = "claude_code"
REJECT_MESSAGE = "Rejected from the agent controller."
SESSION_SUGGESTION_TYPES = {"addRules", "addDirectories"}
# Events that mean any question still showing for this session was answered in the terminal.
TURN_OVER = {"Stop", "StopFailure", "UserPromptSubmit", "SessionEnd"}
TOOL_DONE = {"PostToolUse", "PostToolUseFailure"}


def summarize(tool_name: str, tool_input: dict) -> str:
    """One line a person can judge an approval by."""
    ti = tool_input or {}
    if tool_name == "Bash":
        return ti.get("command", "")
    if tool_name in ("Edit", "MultiEdit", "Write", "Read", "NotebookEdit"):
        return ti.get("file_path") or ti.get("notebook_path", "")
    if tool_name == "WebFetch":
        return ti.get("url", "")
    if tool_name == "WebSearch":
        return ti.get("query", "")
    if tool_name in ("Glob", "Grep"):
        return ti.get("pattern", "")
    if tool_name in ("Task", "Agent"):
        return ti.get("description", "")
    return json.dumps(ti, separators=(",", ":"))[:300]


def decision_output(choice: Choice | None, suggestions: list | None) -> dict:
    """The JSON body Claude Code expects back from a PermissionRequest hook."""
    if choice in (None, Choice.ASK_TERMINAL):
        return {}  # no decision: Claude Code shows its own prompt
    if choice == Choice.REJECT:
        decision = {"behavior": "deny", "message": REJECT_MESSAGE}
    else:
        decision = {"behavior": "allow"}
        if choice == Choice.APPROVE_SESSION:
            # Claude Code's own suggested rules, but only for this session (never written to a file),
            # and never a mode change (a "setMode" suggestion switched the Mac Mini to accept-edits).
            updates = [{**s, "destination": "session"} for s in suggestions or []
                       if isinstance(s, dict) and s.get("type") in SESSION_SUGGESTION_TYPES]
            if updates:
                decision["updatedPermissions"] = updates
    return {"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": decision}}


class ClaudeCode:
    name = NAME
    caps = {Cap.STATUS, Cap.APPROVE, Cap.FOCUS}

    def __init__(self):
        self.app = None
        self._ids = itertools.count(1)
        self._last_ts: dict[str, float] = {}  # newest status event applied, per session

    def _clear_answered(self, ev: str, p: dict, ts: float) -> None:
        """Claude Code shows its own menu while our hook waits; if you answer there, nothing
        tells us. So when the session moves past the question, take it off the device."""
        sid = p["session_id"]
        for a in [a for a in self.app.state.approvals if a.session_id == sid]:
            if ts and a.fired_ts and ts <= a.fired_ts:
                continue  # this event happened before the question (async hooks can arrive late)
            same_tool = (p.get("tool_name") == a.tool_name and (p.get("tool_input") or {}) == a.tool_input)
            if ev in TURN_OVER or (ev in TOOL_DONE and same_tool):
                self.app.withdraw_approval(a)
                self.app.toast("Answered in the terminal")

    async def start(self, app) -> None:
        self.app = app

    # ---- hook events -------------------------------------------------------------
    async def handle_hook(self, p: dict) -> dict:
        ev = p.get("hook_event_name")
        sid = p.get("session_id")
        if not ev or not sid:
            return {}
        cwd = p.get("cwd")
        app = self.app

        if ev == "PermissionRequest":
            return await self._permission(p)

        ts = p.get("_ts") or 0.0
        self._clear_answered(ev, p, ts)
        if ts and ev != "SessionEnd":
            if ts < self._last_ts.get(sid, 0.0):
                return {}  # an older event that arrived late: don't let it overwrite newer status
            self._last_ts[sid] = ts

        if ev == "SessionStart":
            new = sid not in app.state.sessions
            app.upsert_session(NAME, sid, cwd, status=Status.IDLE if new else None, term=p.get("_term") or None)
        elif ev == "UserPromptSubmit":
            app.upsert_session(NAME, sid, cwd, status=Status.WORKING, text="> " + (p.get("prompt") or "")[:300],
                               tool="")
        elif ev == "PreToolUse":
            tool = p.get("tool_name", "")
            app.upsert_session(NAME, sid, cwd, status=Status.WORKING,
                               tool=f"{tool}: {summarize(tool, p.get('tool_input'))}"[:200])
        elif ev in ("PostToolUse", "PostToolUseFailure"):
            app.upsert_session(NAME, sid, cwd, status=Status.WORKING)
        elif ev == "Notification":
            kind = p.get("notification_type")
            if kind in ("permission_prompt", "agent_needs_input", "elicitation_dialog", "elicitation_url_dialog"):
                app.upsert_session(NAME, sid, cwd, status=Status.WAITING, text=p.get("message") or None)
            else:
                app.upsert_session(NAME, sid, cwd)
        elif ev == "Stop":
            app.upsert_session(NAME, sid, cwd, status=Status.DONE, tool="",
                               text=(p.get("last_assistant_message") or "")[:2000] or None)
        elif ev == "StopFailure":
            app.upsert_session(NAME, sid, cwd, status=Status.ERROR,
                               text=(p.get("last_assistant_message") or p.get("error") or "")[:500] or None)
        elif ev == "SessionEnd":
            app.end_session(sid)
            self._last_ts.pop(sid, None)
        return {}

    async def _permission(self, p: dict) -> dict:
        app = self.app
        sid = p["session_id"]
        app.upsert_session(NAME, sid, p.get("cwd"))
        if not app.has_input_device:
            return {}  # nobody to ask: straight to Claude Code's prompt
        tool = p.get("tool_name", "")
        suggestions = p.get("permission_suggestions") or []
        fut = asyncio.get_running_loop().create_future()
        a = Approval(id=f"pr-{next(self._ids)}", session_id=sid, tool_name=tool,
                     summary=summarize(tool, p.get("tool_input")), tool_input=p.get("tool_input") or {},
                     suggestions=suggestions, future=fut, fired_ts=p.get("_ts") or 0.0)
        app.add_approval(a)
        try:
            choice = await asyncio.wait_for(asyncio.shield(fut), timeout=app.cfg.approval_timeout_s)
        except asyncio.TimeoutError:
            app.withdraw_approval(a)
            app.toast("No answer — asking in the terminal")
            return {}
        except asyncio.CancelledError:  # Claude Code hung up (e.g. Esc in the terminal)
            app.withdraw_approval(a)
            raise
        log.info("approval %s (%s %s) -> %s", a.id, tool, a.summary[:60], choice)
        return decision_output(choice, suggestions)

    # ---- actions -------------------------------------------------------------------
    async def send_prompt(self, sid: str, text: str) -> None:  # M2 (voice)
        raise NotImplementedError

    async def decide(self, sid: str, request_id: str, choice: Choice) -> None:
        for a in self.app.state.approvals:
            if a.id == request_id:
                self.app._settle(a, choice)

    async def focus(self, sid: str) -> bool:
        s = self.app.state.sessions.get(sid)
        term = s.term if s else {}
        if sys.platform == "darwin":
            from ...osx.focus import focus_terminal
        elif sys.platform == "win32":
            from ...win.focus import focus_terminal
        else:
            return False
        ok = await asyncio.to_thread(focus_terminal, term or {})
        if not ok:
            self.app.toast("Couldn't find that terminal")
        return ok
