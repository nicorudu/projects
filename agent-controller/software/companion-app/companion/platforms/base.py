"""The contract every platform plug-in follows (docs/architecture.md section 8)."""

from __future__ import annotations

from enum import Enum
from typing import Protocol

from ..core.state import Choice


class Cap(str, Enum):
    STATUS = "status"  # reports sessions and their status
    APPROVE = "approve"  # approvals can be answered from the device
    PROMPT = "prompt"  # can deliver a typed/spoken prompt
    FOCUS = "focus"  # can bring the session's window to the front


class Platform(Protocol):
    name: str
    caps: set[Cap]

    async def start(self, app) -> None: ...
    async def send_prompt(self, sid: str, text: str) -> None: ...
    async def decide(self, sid: str, request_id: str, choice: Choice) -> None: ...
    async def focus(self, sid: str) -> bool: ...
