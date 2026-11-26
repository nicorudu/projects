"""The one source of truth. Plain dataclasses; only core/app.py changes them."""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum


class Status(str, Enum):
    WORKING = "working"
    WAITING = "waiting"
    DONE = "done"
    ERROR = "error"
    READY = "ready"  # open at its prompt, nothing asked yet
    IDLE = "idle"  # nothing has happened for a while (Config.idle_after_s)


class Screen(str, Enum):
    HOME = "home"
    DETAIL = "detail"
    APPROVAL = "approval"
    VOICE = "voice"


class Choice(str, Enum):
    APPROVE = "approve"
    APPROVE_SESSION = "approve_session"
    REJECT = "reject"
    ASK_TERMINAL = "ask_terminal"  # no decision: Claude Code shows its normal prompt


APPROVAL_OPTIONS: list[tuple[Choice, str]] = [
    (Choice.APPROVE, "Approve"),
    (Choice.APPROVE_SESSION, "Approve for session"),
    (Choice.REJECT, "Reject"),
    (Choice.ASK_TERMINAL, "Ask in terminal"),
]

# Waiting first, then errors, then working, then the rest.
STATUS_ORDER = {Status.WAITING: 0, Status.ERROR: 1, Status.WORKING: 2, Status.DONE: 3, Status.READY: 4,
                Status.IDLE: 5}
IN_TURN = (Status.WORKING, Status.WAITING)  # the agent is in the middle of a turn


@dataclass
class Session:
    id: str
    platform: str
    cwd: str = ""  # where the session is working now; follows every `cd`
    home: str = ""  # where it was started; this, not cwd, decides what it is called
    home_known: bool = False  # True once the platform told us; until then home is the first cwd seen
    name: str = ""  # the project: repo name from the git remote, else the folder name
    title: str = ""  # the task: a short form of the first prompt; "" until there is one
    repo: str = ""  # repo label for home (core/names.py), "" if none or not looked up yet
    status: Status = Status.READY
    since: float = field(default_factory=time.time)  # when the status last changed
    turn_started: float | None = None  # when the current turn began; None between turns
    worked_s: float | None = None  # how long the last finished turn took
    tool: str = ""  # current or last tool, summarized
    text: str = ""  # last prompt / last reply, shortened
    term: dict = field(default_factory=dict)  # terminal app + tab, for focus


@dataclass
class Approval:
    id: str
    session_id: str
    tool_name: str
    summary: str
    tool_input: dict
    suggestions: list
    future: asyncio.Future
    created: float = field(default_factory=time.time)
    fired_ts: float = 0.0  # when Claude Code fired the hook (its `_ts`), for ordering against other events


@dataclass
class Focus:
    screen: Screen = Screen.HOME
    sel: int = 0  # selected row on Home, used when sel_id is unknown or gone
    sel_id: str | None = None  # the selected session; the highlight stays on it when rows reorder
    detail_id: str | None = None
    scroll: int = 0
    scroll_max: int | None = None  # the device's limit for the detail page showing; None = not told yet
    approval_sel: int = 0
    return_to: Screen = Screen.HOME  # where to go after the approval queue empties


@dataclass
class State:
    sessions: "OrderedDict[str, Session]" = field(default_factory=OrderedDict)
    approvals: list[Approval] = field(default_factory=list)  # queue, oldest first
    focus: Focus = field(default_factory=Focus)
    voice: str = "idle"  # idle -> recording -> transcribing -> review -> sending (M2)

    def visible_sessions(self) -> list[Session]:
        # Grouped by status (STATUS_ORDER); newest change first inside each group.
        return sorted(self.sessions.values(), key=lambda s: (STATUS_ORDER[s.status], -s.since))

    def selected_index(self, rows: list[Session] | None = None) -> int:
        rows = self.visible_sessions() if rows is None else rows
        for i, s in enumerate(rows):
            if s.id == self.focus.sel_id:
                return i
        return min(self.focus.sel, max(len(rows) - 1, 0))

    def selected_session(self) -> Session | None:
        rows = self.visible_sessions()
        if not rows:
            return None
        return rows[self.selected_index(rows)]
