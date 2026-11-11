from companion.core import intents
from companion.core.state import Screen, Session, State, Status
from companion.view import builder


def test_every_screen_has_cancel_or_back_where_documented():
    assert intents.resolve(Screen.APPROVAL, "cancel") == "reject"
    assert intents.resolve(Screen.DETAIL, "cancel") == "go_home"
    assert intents.resolve(Screen.HOME, "cancel") is None  # documented as "—"
    assert intents.resolve(Screen.APPROVAL, "voice_down") is None


def test_home_orders_waiting_first_and_filters():
    st = State()
    st.sessions["a"] = Session("a", "claude_code", name="a", status=Status.DONE, since=3)
    st.sessions["b"] = Session("b", "claude_code", name="b", status=Status.WAITING, since=1)
    st.sessions["c"] = Session("c", "claude_code", name="c", status=Status.WORKING, since=2)
    v = builder.build(st)
    assert [r["id"] for r in v["rows"]] == ["b", "c", "a"]
    assert v["header"] == {"waiting": 1, "working": 1, "approvals": 0}
    st.focus.filter = "waiting"
    assert [r["id"] for r in builder.build(st)["rows"]] == ["b"]


def test_diff_view_then_patch_then_nothing():
    st = State()
    st.sessions["a"] = Session("a", "claude_code", name="a")
    v1 = builder.build(st)
    m1 = builder.diff(None, v1)
    assert m1["t"] == "view"
    st.focus.filter = "done"
    v2 = builder.build(st)
    m2 = builder.diff(v1, v2)
    assert m2["t"] == "patch" and m2["set"] == {"filter": "done"}
    assert builder.diff(v2, builder.build(st)) is None
    # a device applying the messages ends up with the same screen
    assert builder.apply(builder.apply(None, m1), m2) == v2


def test_led_priority():
    st = State()
    assert builder.led_mode(st) == "idle"
    st.sessions["a"] = Session("a", "x", status=Status.WORKING)
    assert builder.led_mode(st) == "working"
    st.sessions["b"] = Session("b", "x", status=Status.WAITING)
    assert builder.led_mode(st) == "waiting"
