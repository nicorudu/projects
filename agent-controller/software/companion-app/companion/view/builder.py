"""Turns State into the screen the dock should show, and works out the smallest update.

The dock only ever draws what it's sent: a full `view` when the screen changes,
a `patch` with just the changed fields otherwise.
"""

from __future__ import annotations

from ..core.state import APPROVAL_OPTIONS, Screen, State, Status
from ..protocol.messages import msg

MAX_TEXT = 400


def _row(s) -> dict:
    return {"id": s.id, "name": s.name, "status": s.status.value, "tool": s.tool[:60], "since": int(s.since)}


def build(state: State) -> dict:
    f = state.focus
    counts = {st.value: 0 for st in Status}
    for s in state.sessions.values():
        counts[s.status.value] += 1
    header = {"waiting": counts["waiting"], "working": counts["working"], "approvals": len(state.approvals)}

    if f.screen == Screen.APPROVAL and state.approvals:
        a = state.approvals[0]
        sess = state.sessions.get(a.session_id)
        return {
            "screen": "approval",
            "id": a.id,
            "session": sess.name if sess else a.session_id[:8],
            "tool": a.tool_name,
            "summary": a.summary[:MAX_TEXT],
            "options": [label for _, label in APPROVAL_OPTIONS],
            "sel": f.approval_sel,
            "queue": len(state.approvals),
        }

    if f.screen == Screen.DETAIL and f.detail_id in state.sessions:
        s = state.sessions[f.detail_id]
        return {
            "screen": "detail",
            "id": s.id,
            "name": s.name,
            "status": s.status.value,
            "since": int(s.since),
            "cwd": s.cwd,
            "tool": s.tool,
            "text": s.text[:MAX_TEXT],
            "scroll": f.scroll,
            "header": header,
        }

    if f.screen == Screen.VOICE:
        return {"screen": "voice", "state": state.voice, "text": "", "header": header}

    rows = state.visible_sessions()
    return {
        "screen": "home",
        "filter": f.filter,
        "sel": min(f.sel, max(len(rows) - 1, 0)),
        "rows": [_row(s) for s in rows],
        "header": header,
    }


def diff(prev: dict | None, new: dict) -> dict | None:
    """The message that turns `prev` into `new`, or None if nothing changed."""
    if prev is None or prev.get("screen") != new.get("screen"):
        return msg("view", **new)
    changed = {k: v for k, v in new.items() if prev.get(k) != v}
    removed = [k for k in prev if k not in new]
    if removed:  # a field disappeared: simplest correct answer is a full redraw
        return msg("view", **new)
    if not changed:
        return None
    return msg("patch", screen=new["screen"], set=changed)


def apply(current: dict | None, m: dict) -> dict:
    """What a device does with view/patch. Used by the fake device and the tests."""
    if m["t"] == "view":
        return {k: v for k, v in m.items() if k not in ("v", "t")}
    if m["t"] == "patch":
        if current is None or current.get("screen") != m["screen"]:
            raise ValueError("patch for a screen that isn't showing")
        return {**current, **m["set"]}
    return current or {}


def led_mode(state: State) -> str:
    if state.voice == "recording":
        return "recording"
    statuses = {s.status for s in state.sessions.values()}
    if state.approvals or Status.WAITING in statuses:
        return "waiting"
    if Status.ERROR in statuses:
        return "error"
    if Status.WORKING in statuses:
        return "working"
    if Status.DONE in statuses:
        return "done"
    return "idle"
