"""What a key press means on each screen. This table is the only place button behavior lives.

Matches docs/architecture.md section 6. Voice actions do nothing useful until M2.
"""

from __future__ import annotations

from .state import Screen

S = Screen

TABLE: dict[tuple[Screen, str], str] = {
    # Home: every session
    (S.HOME, "up"): "sel_prev",
    (S.HOME, "down"): "sel_next",
    (S.HOME, "left"): "filter_prev",
    (S.HOME, "right"): "filter_next",
    (S.HOME, "click"): "open_detail",
    (S.HOME, "voice_down"): "voice_start",
    (S.HOME, "voice_up"): "voice_stop",
    (S.HOME, "send"): "focus_session",
    # Detail: one session
    (S.DETAIL, "up"): "scroll_up",
    (S.DETAIL, "down"): "scroll_down",
    (S.DETAIL, "left"): "detail_prev",
    (S.DETAIL, "right"): "detail_next",
    (S.DETAIL, "click"): "go_home",
    (S.DETAIL, "cancel"): "go_home",
    (S.DETAIL, "voice_down"): "voice_start",
    (S.DETAIL, "voice_up"): "voice_stop",
    (S.DETAIL, "send"): "focus_session",
    # Approval: pops up when an agent asks
    (S.APPROVAL, "up"): "option_prev",
    (S.APPROVAL, "down"): "option_next",
    (S.APPROVAL, "left"): "option_prev",
    (S.APPROVAL, "right"): "option_next",
    (S.APPROVAL, "click"): "confirm_option",
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
