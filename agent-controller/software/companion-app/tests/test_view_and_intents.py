import time

from companion.core import intents
from companion.core.state import Screen, Session, State, Status
from companion.protocol.messages import INPUTS
from companion.view import builder

# Blueprint rev 3 section 7.1, one row per screen. Anything not listed must do nothing.
CONTROLS = {
    Screen.HOME: {"up": "sel_prev", "down": "sel_next", "right": "open_detail", "send": "focus_session",
                  "voice_down": "voice_start", "voice_up": "voice_stop", "green": "go_home"},
    Screen.DETAIL: {"up": "scroll_up", "down": "scroll_down", "left": "go_home", "cancel": "go_home",
                    "send": "focus_session", "voice_down": "voice_start", "voice_up": "voice_stop",
                    "green": "go_home"},
    Screen.APPROVAL: {"up": "option_prev", "down": "option_next", "send": "confirm_option",
                      "cancel": "reject"},
    Screen.VOICE: {"cancel": "voice_discard", "send": "voice_deliver", "voice_down": "voice_start",
                   "voice_up": "voice_stop"},
}


def test_controls_match_the_blueprint_table():
    for screen in Screen:
        for inp in INPUTS:
            assert intents.resolve(screen, inp) == CONTROLS[screen].get(inp), (screen, inp)
    assert set(intents.TABLE) == {(s, i) for s, row in CONTROLS.items() for i in row}


def test_there_is_no_stick_click_and_only_send_confirms():
    assert "click" not in INPUTS and "green" in INPUTS
    confirming = [inp for inp in INPUTS if intents.resolve(Screen.APPROVAL, inp) == "confirm_option"]
    assert confirming == ["send"]  # a stray flick can never approve
    assert intents.resolve(Screen.APPROVAL, "left") is None
    assert intents.resolve(Screen.APPROVAL, "right") is None


def test_home_orders_by_status():
    st = State()
    st.sessions["a"] = Session("a", "claude_code", name="a", status=Status.DONE, since=3)
    st.sessions["b"] = Session("b", "claude_code", name="b", status=Status.WAITING, since=1)
    st.sessions["c"] = Session("c", "claude_code", name="c", status=Status.WORKING, since=2)
    st.sessions["d"] = Session("d", "claude_code", name="d", status=Status.IDLE, since=5)
    st.sessions["e"] = Session("e", "claude_code", name="e", status=Status.READY, since=4)
    st.sessions["f"] = Session("f", "claude_code", name="f", status=Status.ERROR, since=6)
    v = builder.build(st)
    assert [r["id"] for r in v["rows"]] == ["b", "f", "c", "a", "e", "d"]
    assert [r["status"] for r in v["rows"]] == ["waiting", "error", "working", "done", "ready", "idle"]
    assert v["header"] == {"waiting": 1, "working": 1, "approvals": 0}
    assert "filter" not in v  # the reference has no filters


def test_selection_stays_on_its_session_when_rows_reorder():
    st = State()
    st.sessions["a"] = Session("a", "x", name="a", status=Status.WORKING, since=2)
    st.sessions["b"] = Session("b", "x", name="b", status=Status.DONE, since=1)
    st.focus.sel, st.focus.sel_id = 1, "b"
    assert builder.build(st)["sel"] == 1
    st.sessions["b"].status = Status.WAITING  # b jumps to the top
    v = builder.build(st)
    assert [r["id"] for r in v["rows"]] == ["b", "a"] and v["sel"] == 0
    assert st.selected_session().id == "b"
    del st.sessions["b"]  # gone: fall back to the remembered row, clamped
    assert builder.build(st)["sel"] == 0 and st.selected_session().id == "a"


def test_detail_shows_time_worked_and_the_whole_last_message():
    st = State()
    now = time.time()
    s = Session("a", "x", name="alpha", status=Status.WORKING, turn_started=now - 90, text="x" * 3000)
    st.sessions["a"] = s
    st.focus.screen, st.focus.detail_id = Screen.DETAIL, "a"
    v = builder.build(st)
    assert v["turn_start"] == int(now - 90) and v["worked_s"] is None
    assert len(v["text"]) == builder.MAX_DETAIL_TEXT
    s.status, s.turn_started, s.worked_s = Status.DONE, None, 384.4
    v = builder.build(st)
    assert v["turn_start"] is None and v["worked_s"] == 384


def test_diff_view_then_patch_then_nothing():
    st = State()
    st.sessions["a"] = Session("a", "claude_code", name="a")
    st.sessions["b"] = Session("b", "claude_code", name="b")
    v1 = builder.build(st)
    m1 = builder.diff(None, v1)
    assert m1["t"] == "view"
    st.focus.sel, st.focus.sel_id = 1, v1["rows"][1]["id"]
    v2 = builder.build(st)
    m2 = builder.diff(v1, v2)
    assert m2["t"] == "patch" and m2["set"] == {"sel": 1}
    assert builder.diff(v2, builder.build(st)) is None
    # a device applying the messages ends up with the same screen
    assert builder.apply(builder.apply(None, m1), m2) == v2


def test_led_priority():
    st = State()
    assert builder.led_mode(st) == "idle"
    st.sessions["r"] = Session("r", "x", status=Status.READY)
    assert builder.led_mode(st) == "idle"
    st.sessions["a"] = Session("a", "x", status=Status.WORKING)
    assert builder.led_mode(st) == "working"
    st.sessions["b"] = Session("b", "x", status=Status.WAITING)
    assert builder.led_mode(st) == "waiting"
