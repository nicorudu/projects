"""M1b: the app behaves like the reference's demo (blueprint rev 3 section 7.1)."""

import asyncio
import dataclasses
import time

from companion.core.app import App
from companion.core.state import Screen, Status
from companion.protocol.messages import encode, msg
from fake_device import FakeDevice, detail_window, worked_line


class FakePlatform:
    """Records focus calls instead of touching real windows."""

    name = "fake"

    def __init__(self):
        self.focused: list[tuple[str, bool]] = []

    async def start(self, app):
        pass

    async def focus(self, sid, quiet=False):
        self.focused.append((sid, quiet))
        return True


async def make_app(cfg, **changes):
    app = App(dataclasses.replace(cfg, **changes))
    plat = FakePlatform()
    app.register_platform(plat)
    await app.start()
    for sid in ("s1", "s2", "s3"):
        app.upsert_session("fake", sid, cwd=f"/p/{sid}", status="working")
        await asyncio.sleep(0.002)  # distinct timestamps, so the row order is fixed
    return app, plat


def order(app):
    return [s.id for s in app.state.visible_sessions()]


async def test_focus_follows_selection_after_the_pause(cfg):
    app, plat = await make_app(cfg, focus_follows_selection=True, focus_follow_delay_s=0.05)
    rows = order(app)
    app.handle_input("down")
    assert plat.focused == []  # not instantly
    await asyncio.sleep(0.15)
    assert plat.focused == [(rows[1], True)]  # quiet: no toast if the window can't be found
    await app.stop()


async def test_flicking_past_rows_only_focuses_where_the_stick_rests(cfg):
    app, plat = await make_app(cfg, focus_follows_selection=True, focus_follow_delay_s=0.08)
    rows = order(app)
    app.handle_input("down")
    await asyncio.sleep(0.02)
    app.handle_input("down")
    await asyncio.sleep(0.2)
    assert plat.focused == [(rows[2], True)]
    app.handle_input("down")  # already on the last row: nothing changes, nothing is focused
    await asyncio.sleep(0.2)
    assert plat.focused == [(rows[2], True)]
    await app.stop()


async def test_focus_does_not_follow_when_switched_off_or_after_leaving_home(cfg):
    app, plat = await make_app(cfg, focus_follows_selection=False)
    app.handle_input("down")
    await asyncio.sleep(0.12)
    assert plat.focused == []
    await app.stop()

    app, plat = await make_app(cfg, focus_follows_selection=True, focus_follow_delay_s=0.08)
    app.handle_input("down")
    app.handle_input("right")  # opened the detail page before the pause ran out
    assert app.state.focus.screen == Screen.DETAIL
    await asyncio.sleep(0.2)
    assert plat.focused == []
    await app.stop()


async def test_send_focuses_now_and_only_once(cfg):
    app, plat = await make_app(cfg, focus_follows_selection=True, focus_follow_delay_s=0.08)
    rows = order(app)
    app.handle_input("down")
    app.handle_input("send")
    await asyncio.sleep(0.2)
    assert plat.focused == [(rows[1], False)]
    await app.stop()


async def test_right_opens_left_goes_back_and_nothing_else_moves(cfg):
    app, _ = await make_app(cfg)
    rows = order(app)
    f = app.state.focus
    app.handle_input("left")  # nothing to go back to on the Agents screen
    app.handle_input("cancel")
    assert f.screen == Screen.HOME
    app.handle_input("down")
    app.handle_input("right")
    assert f.screen == Screen.DETAIL and f.detail_id == rows[1]
    app.handle_input("right")  # no next/previous session from the detail page
    assert f.screen == Screen.DETAIL and f.detail_id == rows[1]
    app.handle_input("left")
    assert f.screen == Screen.HOME and app.state.selected_session().id == rows[1]
    await app.stop()


async def test_selected_session_keeps_the_highlight_when_it_changes_status(cfg):
    app, _ = await make_app(cfg)
    rows = order(app)
    app.handle_input("down")
    app.handle_input("down")
    assert app.state.selected_session().id == rows[2]
    app.upsert_session("fake", rows[2], status="waiting")  # jumps to the top of the list
    assert order(app)[0] == rows[2] and app.state.selected_index() == 0
    app.end_session(rows[2])  # the highlight stays on the same row
    assert app.state.selected_index() == 0 and app.state.selected_session().id == order(app)[0]
    await app.stop()


async def test_status_words_ready_then_working_done_and_idle(cfg):
    app, _ = await make_app(cfg, idle_after_s=0.05)
    s = app.upsert_session("fake", "new")
    assert s.status == Status.READY and s.turn_started is None
    app.upsert_session("fake", "new", status="working")
    assert s.turn_started is not None
    app.upsert_session("fake", "new", status="waiting")  # still the same turn
    started = s.turn_started
    app.upsert_session("fake", "new", status="working")
    assert s.turn_started == started
    s.turn_started = time.time() - 384
    app.upsert_session("fake", "new", status="done")
    assert s.status == Status.DONE and s.turn_started is None and 383 < s.worked_s < 386
    await asyncio.sleep(0.4)  # the watchdog ages quiet sessions
    assert s.status == Status.IDLE
    assert app.state.sessions["s1"].status == Status.WORKING  # a running session never goes idle
    app.upsert_session("fake", "new", status="working")  # a new prompt wakes it
    assert s.status == Status.WORKING and s.worked_s is not None
    await app.stop()


async def test_fake_device_shows_the_reference_screens(running):
    app, url = running
    dev = FakeDevice(url)
    await dev.connect()
    s = app.upsert_session("claude_code", "s1", cwd="/Users/nico/projects/alpha", status="working")
    s.turn_started = time.time() - 384
    app.upsert_session("claude_code", "s1", status="done", text="word " * 300)
    await dev.wait_for(lambda d: d.view["rows"] and d.view["rows"][0]["status"] == "done")
    await dev.send_input("right")
    await dev.wait_for(lambda d: d.view["screen"] == "detail")
    assert worked_line(dev.view) == "Worked for 6m 24s"
    shown, top, total = detail_window(dev.view["text"], dev.view["scroll"])
    assert top == 0 and total > len(shown)
    for _ in range(3):
        await dev.send_input("down")
    await dev.wait_for(lambda d: d.view["scroll"] == 3)
    assert detail_window(dev.view["text"], 3)[1] == 3
    assert detail_window(dev.view["text"], 10_000)[1] == total - len(shown)  # scrolling stops at the end
    await dev.close()


async def test_detail_scroll_stops_where_the_device_says(running):
    app, url = running
    dev = FakeDevice(url)
    await dev.connect()
    app.upsert_session("claude_code", "s1", cwd="/p/alpha", status="done", text="long text")
    await dev.wait_for(lambda d: d.view["rows"])
    await dev.send_input("right")
    await dev.wait_for(lambda d: d.view["screen"] == "detail")
    f = app.state.focus
    for _ in range(5):  # nobody has said where the end is yet, so it just counts
        await dev.send_input("down")
    await dev.wait_for(lambda d: d.view["scroll"] == 5)

    await dev.ws.send(encode(msg("layout", screen="detail", id="other", max_scroll=0)))  # a page we left
    await dev.ws.send(encode(msg("layout", screen="detail", id="s1", max_scroll=2)))
    await dev.wait_for(lambda d: d.view["scroll"] == 2)  # pulled back to the end
    seq = await dev.send_input("down")
    await dev.wait_for(lambda d: seq in d.acks)
    assert f.scroll == 2 and f.scroll_max == 2

    await dev.send_input("left")
    await dev.send_input("right")  # opening a page forgets the old limit
    await dev.wait_for(lambda d: d.view["screen"] == "detail" and d.view["scroll"] == 0)
    assert f.scroll_max is None
    await dev.ws.send(encode(msg("layout", screen="detail", id="s1", max_scroll=-1)))  # nonsense is dropped
    await asyncio.sleep(0.05)
    assert f.scroll_max is None
    await dev.close()


def test_worked_line_formats():
    assert worked_line({"turn_start": 1000, "worked_s": None}, now=1045) == "Working for 45s"
    assert worked_line({"turn_start": None, "worked_s": 384}) == "Worked for 6m 24s"
    assert worked_line({"turn_start": None, "worked_s": 3725}) == "Worked for 1h 2m"
    assert worked_line({"turn_start": None, "worked_s": None}) == ""
