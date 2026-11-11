"""Claude Code hooks end to end: simulated hook POSTs -> app -> fake device -> hook response.

The payloads match the examples in code.claude.com/docs/en/hooks.
"""

import asyncio
import dataclasses
import io
import json
import sys

import aiohttp
import pytest

from companion.core.app import App
from companion.hooks import report
from companion.hooks.server import HookServer
from companion.platforms.claude_code.attached import REJECT_MESSAGE, ClaudeCode
from companion.transports.websocket import WebSocketTransport
from fake_device import FakeDevice

SID = "abc123"
SUGGESTIONS = [{"type": "addRules", "rules": [{"toolName": "Bash", "ruleContent": "rm -rf node_modules"}],
                "behavior": "allow", "destination": "localSettings"}]


def perm_request(sid=SID, cmd="rm -rf node_modules"):
    return {"session_id": sid, "transcript_path": "/tmp/t.jsonl", "cwd": "/Users/nico/projects/alpha",
            "permission_mode": "default", "hook_event_name": "PermissionRequest", "tool_name": "Bash",
            "tool_input": {"command": cmd, "description": "Remove node_modules directory"},
            "permission_suggestions": SUGGESTIONS}


@pytest.fixture
async def stack(cfg):
    """App + WebSocket + hook server + a connected fake device."""
    async def make(**cfg_changes):
        c = dataclasses.replace(cfg, **cfg_changes)
        app = App(c)
        claude = ClaudeCode()
        app.register_platform(claude)
        ws = WebSocketTransport(app, "127.0.0.1", 0)
        hooks = HookServer(claude, "127.0.0.1", 0)
        await app.start()
        await ws.start()
        await hooks.start()
        made.append((app, ws, hooks))
        return app, f"ws://127.0.0.1:{ws.port}", f"http://127.0.0.1:{hooks.port}/hooks/claude"

    made = []
    yield make
    for app, ws, hooks in made:
        await hooks.stop()
        await ws.stop()
        await app.stop()


async def post(url, payload, timeout=10.0):
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
            assert r.status == 200
            return await r.json()


async def device(url) -> FakeDevice:
    d = FakeDevice(url)
    await d.connect()
    return d


# ---- status ---------------------------------------------------------------------------
async def test_status_events_drive_the_home_screen(stack):
    app, ws_url, hook_url = await stack()
    dev = await device(ws_url)
    base = {"session_id": SID, "cwd": "/Users/nico/projects/alpha", "transcript_path": "/tmp/t"}
    assert await post(hook_url, {**base, "hook_event_name": "UserPromptSubmit", "prompt": "fix the bug"}) == {}
    await post(hook_url, {**base, "hook_event_name": "PreToolUse", "tool_name": "Bash",
                          "tool_input": {"command": "npm test"}, "tool_use_id": "t1"})
    await dev.wait_for(lambda d: d.view["rows"] and d.view["rows"][0]["tool"] == "Bash: npm test")
    assert dev.view["rows"][0]["name"] == "alpha" and dev.view["rows"][0]["status"] == "working"
    assert dev.led == "working"

    await post(hook_url, {**base, "hook_event_name": "Notification", "notification_type": "permission_prompt",
                          "message": "Claude needs your permission"})
    await dev.wait_for(lambda d: d.view["rows"][0]["status"] == "waiting" and d.led == "waiting")
    assert dev.sounds >= 1

    await post(hook_url, {**base, "hook_event_name": "Stop", "stop_hook_active": False,
                          "last_assistant_message": "All tests pass."})
    await dev.wait_for(lambda d: d.view["rows"][0]["status"] == "done")
    assert app.state.sessions[SID].text == "All tests pass."

    await post(hook_url, {**base, "hook_event_name": "SessionEnd", "reason": "other"})
    await dev.wait_for(lambda d: d.view["rows"] == [])
    await dev.close()


# ---- approvals ------------------------------------------------------------------------
async def answer(stack_make, *keys, **cfg_changes):
    """Post a PermissionRequest, press keys on the fake device once the Approval screen is up."""
    app, ws_url, hook_url = await stack_make(**cfg_changes)
    dev = await device(ws_url)
    pending = asyncio.create_task(post(hook_url, perm_request()))
    # view and led are separate frames; wait for both (on a fast machine the led can trail the view)
    await dev.wait_for(lambda d: d.view["screen"] == "approval" and d.led == "waiting")
    assert dev.view["tool"] == "Bash" and dev.view["summary"] == "rm -rf node_modules"
    assert dev.view["options"] == ["Approve", "Approve for session", "Reject", "Ask in terminal"]
    for k in keys:
        await dev.send_input(k)
    result = await asyncio.wait_for(pending, 5)
    await dev.wait_for(lambda d: d.view["screen"] == "home")
    await dev.close()
    return result, app, dev


async def test_approve(stack):
    result, app, dev = await answer(stack, "click")
    assert result == {"hookSpecificOutput": {"hookEventName": "PermissionRequest",
                                             "decision": {"behavior": "allow"}}}
    assert "Approved" in dev.toasts
    assert app.state.sessions[SID].status.value == "working"


async def test_approve_for_session_scopes_rules_to_session(stack):
    result, *_ = await answer(stack, "down", "send")
    d = result["hookSpecificOutput"]["decision"]
    assert d["behavior"] == "allow"
    assert d["updatedPermissions"] == [{**SUGGESTIONS[0], "destination": "session"}]


async def test_reject_with_cancel_key(stack):
    result, *_ = await answer(stack, "cancel")
    assert result["hookSpecificOutput"]["decision"] == {"behavior": "deny", "message": REJECT_MESSAGE}


async def test_ask_in_terminal_returns_no_decision(stack):
    result, *_ = await answer(stack, "up", "click")  # wraps from Approve to "Ask in terminal"
    assert result == {}


async def test_no_device_means_terminal_prompt_immediately(stack):
    app, ws_url, hook_url = await stack()
    assert await asyncio.wait_for(post(hook_url, perm_request()), 2) == {}
    assert app.state.approvals == []


async def test_device_disconnect_releases_approval(stack):
    app, ws_url, hook_url = await stack()
    dev = await device(ws_url)
    pending = asyncio.create_task(post(hook_url, perm_request()))
    await dev.wait_for(lambda d: d.view["screen"] == "approval")
    await dev.close()
    assert await asyncio.wait_for(pending, 3) == {}
    assert app.state.approvals == []


async def test_timeout_returns_no_decision(stack):
    app, ws_url, hook_url = await stack(approval_timeout_s=0.4)
    dev = await device(ws_url)
    assert await asyncio.wait_for(post(hook_url, perm_request()), 3) == {}
    await dev.wait_for(lambda d: d.view["screen"] == "home")
    assert any("terminal" in t for t in dev.toasts)
    await dev.close()


async def test_two_requests_queue_in_order(stack):
    app, ws_url, hook_url = await stack()
    dev = await device(ws_url)
    first = asyncio.create_task(post(hook_url, perm_request(cmd="first")))
    await dev.wait_for(lambda d: d.view["screen"] == "approval")
    second = asyncio.create_task(post(hook_url, perm_request(sid="other", cmd="second")))
    await dev.wait_for(lambda d: d.view.get("queue") == 2)
    assert dev.view["summary"] == "first"
    await dev.send_input("click")
    assert (await asyncio.wait_for(first, 3))["hookSpecificOutput"]["decision"]["behavior"] == "allow"
    await dev.wait_for(lambda d: d.view.get("summary") == "second")
    await dev.send_input("cancel")
    assert (await asyncio.wait_for(second, 3))["hookSpecificOutput"]["decision"]["behavior"] == "deny"
    await dev.close()


async def test_claude_hanging_up_withdraws_the_approval(stack):
    app, ws_url, hook_url = await stack()
    dev = await device(ws_url)
    with pytest.raises(asyncio.TimeoutError):
        await post(hook_url, perm_request(), timeout=0.4)  # e.g. Esc pressed in the terminal
    await dev.wait_for(lambda d: d.view["screen"] == "home", timeout=3)
    assert app.state.approvals == []
    await dev.close()


# ---- hook server hygiene ---------------------------------------------------------------
async def test_rejects_foreign_host_and_non_json(stack):
    app, ws_url, hook_url = await stack()
    async with aiohttp.ClientSession() as s:
        async with s.post(hook_url, json={}, headers={"Host": "evil.example"}) as r:
            assert r.status == 403
        async with s.post(hook_url, data="session_id=x", headers={"Content-Type": "text/plain"}) as r:
            assert r.status == 415
        async with s.get(hook_url.replace("/hooks/claude", "/health")) as r:
            assert (await r.json())["ok"] is True


async def test_session_start_report_script_adds_terminal_info(stack, monkeypatch):
    app, ws_url, hook_url = await stack()
    payload = {"session_id": SID, "cwd": "/Users/nico/projects/alpha", "hook_event_name": "SessionStart",
               "source": "startup"}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setenv("TERM_PROGRAM", "Apple_Terminal")
    monkeypatch.setenv("__CFBundleIdentifier", "com.apple.Terminal")
    assert await asyncio.to_thread(report.main, ["--url", hook_url]) == 0
    s = app.state.sessions[SID]
    assert s.term["term_program"] == "Apple_Terminal" and s.term["bundle_id"] == "com.apple.Terminal"
    assert s.status.value == "idle"


def test_report_script_is_silent_when_app_is_down(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"session_id":"x"}'))
    assert report.main(["--url", "http://127.0.0.1:9/hooks/claude"]) == 0
