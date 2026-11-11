"""Bring a session's window forward on Windows. Not built yet (Mac Mini comes first).

Plan: pywinauto / SetForegroundWindow on the window that owns the Claude Code process,
using WT_SESSION for Windows Terminal tabs.
"""

from __future__ import annotations


def focus_terminal(term: dict) -> bool:
    return False
