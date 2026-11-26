"""What a key press means on each screen. This table is the only place button behavior lives.

Matches docs/architecture.md section 6 and blueprint rev 3 section 7.1 (the reference's controls):
stick right opens, stick left goes back, only Send confirms, and there is no stick click.
A pair that is missing from the table does nothing. Voice actions do nothing useful until M2.
"""

from __future__ import annotations

from .state import Screen

S = Screen

TABLE: dict[tuple[Screen, str], str] = {
    # Agents (home): every session
    (S.HOME, "up"): "sel_prev",
    (S.HOME, "down"): "sel_next",
    (S.HOME, "right"): "open_detail",
    (S.HOME, "send"): "focus_session",
    (S.HOME, "voice_down"): "voice_start",
    (S.HOME, "voice_up"): "voice_stop",
    (S.HOME, "green"): "go_home",
    # Detail: one session
    (S.DETAIL, "up"): "scroll_up",
    (S.DETAIL, "down"): "scroll_down",
    (S.DETAIL, "left"): "go_home",
    (S.DETAIL, "cancel"): "go_home",
    (S.DETAIL, "send"): "focus_session",
    (S.DETAIL, "voice_down"): "voice_start",
    (S.DETAIL, "voice_up"): "voice_stop",
    (S.DETAIL, "green"): "go_home",
    # Approval: pops up when an agent asks. Only Send confirms, so a stray flick can't approve.
    (S.APPROVAL, "up"): "option_prev",
    (S.APPROVAL, "down"): "option_next",
    (S.APPROVAL, "send"): "confirm_option",
    (S.APPROVAL, "cancel"): "reject",
    # Voice review (M2)
    (S.VOICE, "cancel"): "voice_discard",
    (S.VOICE, "voice_down"): "voice_start",
    (S.VOICE, "voice_up"): "voice_stop",
    (S.VOICE, "send"): "voice_deliver",
}


def resolve(screen: Screen, inp: str) -> str | None:
    return TABLE.get((screen, inp))
