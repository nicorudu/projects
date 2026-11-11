"""The fake device against the real app over a real WebSocket."""

import asyncio

from websockets.asyncio.client import connect

from companion.protocol.messages import decode, encode, msg
from fake_device import FakeDevice


async def test_handshake_and_home_screen(running):
    app, url = running
    dev = FakeDevice(url)
    await dev.connect()
    assert dev.view["screen"] == "home" and dev.view["rows"] == []
    assert len(app.links) == 1
    await dev.close()


async def test_sessions_render_and_stick_moves_selection(running):
    app, url = running
    dev = FakeDevice(url)
    await dev.connect()
    app.upsert_session("claude_code", "s1", cwd="/Users/nico/projects/alpha", status="working", tool="Bash: ls")
    app.upsert_session("claude_code", "s2", cwd="/Users/nico/projects/beta", status="done")
    await dev.wait_for(lambda d: len(d.view["rows"]) == 2)
    assert [r["name"] for r in dev.view["rows"]] == ["alpha", "beta"]
    assert dev.led == "working"

    seq = await dev.send_input("down")
    await dev.wait_for(lambda d: d.view["sel"] == 1 and seq in d.acks)
    await dev.send_input("click")
    await dev.wait_for(lambda d: d.view["screen"] == "detail")
    assert dev.view["name"] == "beta"
    await dev.send_input("cancel")
    await dev.wait_for(lambda d: d.view["screen"] == "home")
    await dev.close()


async def test_duplicate_input_is_acked_but_ignored(running):
    app, url = running
    app.upsert_session("claude_code", "s1", cwd="/a", status="idle")
    app.upsert_session("claude_code", "s2", cwd="/b", status="idle")
    app.upsert_session("claude_code", "s3", cwd="/c", status="idle")
    dev = FakeDevice(url)
    await dev.connect()
    for _ in range(2):  # same seq twice, like a resend after a lost ack
        await dev.ws.send(encode(msg("input", seq=7, ts=1, **{"in": "down"})))
    await dev.wait_for(lambda d: 7 in d.acks)
    await asyncio.sleep(0.05)
    assert app.state.focus.sel == 1
    await dev.close()


async def test_hello_required(running):
    app, url = running
    async with connect(url) as ws:
        await ws.send(encode(msg("ping", ts=1)))
        await asyncio.sleep(0.1)
    assert app.links == {}


async def test_heartbeat_timeout_drops_device(running):
    app, url = running
    dev = FakeDevice(url)
    await dev.connect()
    assert len(app.links) == 1
    dev.stop_heartbeat()
    for _ in range(40):
        if not app.links:
            break
        await asyncio.sleep(0.05)
    assert app.links == {}
    await dev.close()


async def test_bad_json_does_not_kill_link(running):
    app, url = running
    dev = FakeDevice(url)
    await dev.connect()
    await dev.ws.send("not json")
    await dev.ws.send('{"v":1,"t":"input","seq":1,"in":"fly"}')
    seq = await dev.send_input("right")
    await dev.wait_for(lambda d: seq in d.acks)
    await dev.wait_for(lambda d: d.view["filter"] == "waiting")
    await dev.close()


def test_welcome_decodes():
    assert decode(encode(msg("welcome", proto=1)))["proto"] == 1
