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
    IDLE = "idle"


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

HOME_FILTERS = ["all", "waiting", "done"]


@dataclass
class Session:
    id: str
    platform: str
    cwd: str = ""
    name: str = ""
    status: Status = Status.IDLE
    since: float = field(default_factory=time.time)  # when the status last changed
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


@dataclass
class Focus:
    screen: Screen = Screen.HOME
    sel: int = 0  # selected row on Home
    filter: str = "all"
    detail_id: str | None = None
    scroll: int = 0
    approval_sel: int = 0
    return_to: Screen = Screen.HOME  # where to go after the approval queue empties


@dataclass
class State:
    sessions: "OrderedDict[str, Session]" = field(default_factory=OrderedDict)
    approvals: list[Approval] = field(default_factory=list)  # queue, oldest first
    focus: Focus = field(default_factory=Focus)
    voice: str = "idle"  # idle -> recording -> transcribing -> review -> sending (M2)

    def visible_sessions(self) -> list[Session]:
        rows = list(self.sessions.values())
        f = self.focus.filter
        if f == "waiting":
            rows = [s for s in rows if s.status == Status.WAITING]
        elif f == "done":
            rows = [s for s in rows if s.status in (Status.DONE, Status.IDLE)]
        # Waiting first, then working, then the rest; newest change first inside each group.
        order = {Status.WAITING: 0, Status.ERROR: 1, Status.WORKING: 2, Status.DONE: 3, Status.IDLE: 4}
        return sorted(rows, key=lambda s: (order[s.status], -s.since))

    def selected_session(self) -> Session | None:
        rows = self.visible_sessions()
        if not rows:
            return None
        return rows[min(self.focus.sel, len(rows) - 1)]
