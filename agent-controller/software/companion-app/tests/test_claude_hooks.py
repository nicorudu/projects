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
    monkeypatch.setenv("TERM_PROGRAM", "Apple_Terminal")
    monkeypatch.setenv("__CFBundleIdentifier", "com.apple.Terminal")
    assert await asyncio.to_thread(report.main, ["--url", hook_url], io.StringIO(json.dumps(payload))) == 0
    s = app.state.sessions[SID]
    assert s.term["term_program"] == "Apple_Terminal" and s.term["bundle_id"] == "com.apple.Terminal"
    assert s.status.value == "idle"


async def test_report_wait_prints_the_decision(stack):
    app, ws_url, hook_url = await stack()
    dev = await device(ws_url)
    out = io.StringIO()
    run = asyncio.create_task(asyncio.to_thread(report.main, ["--url", hook_url, "--wait"],
                                                io.StringIO(json.dumps(perm_request())), out))
    await dev.wait_for(lambda d: d.view["screen"] == "approval")
    await dev.send_input("click")
    assert await asyncio.wait_for(run, 5) == 0
    assert json.loads(out.getvalue())["hookSpecificOutput"]["decision"] == {"behavior": "allow"}
    await dev.close()


@pytest.mark.parametrize("args", [["--wait"], []])
def test_report_script_is_silent_when_app_is_down(args):
    out = io.StringIO()
    assert report.main(["--url", "http://127.0.0.1:9/hooks/claude", *args], io.StringIO(json.dumps(perm_request())),
                       out) == 0
    assert out.getvalue() == ""  # no output = no decision = Claude Code's normal prompt, and no error line


# ---- fixes from the Mac Mini test (2026-11-11) -------------------------------------------
async def test_approve_for_session_never_changes_the_mode(stack):
    app, ws_url, hook_url = await stack()
    dev = await device(ws_url)
    suggestions = [{"type": "setMode", "mode": "acceptEdits", "destination": "session"},
                   {"type": "addDirectories", "directories": ["/Users/nico"], "destination": "localSettings"},
                   {"type": "addRules", "rules": [{"toolName": "Bash", "ruleContent": "touch:*"}],
                    "behavior": "allow", "destination": "localSettings"}]
    pending = asyncio.create_task(post(hook_url, {**perm_request(), "permission_suggestions": suggestions}))
    await dev.wait_for(lambda d: d.view["screen"] == "approval")
    await dev.send_input("down")
    await dev.send_input("click")
    d = (await asyncio.wait_for(pending, 3))["hookSpecificOutput"]["decision"]
    assert [u["type"] for u in d["updatedPermissions"]] == ["addDirectories", "addRules"]
    assert all(u["destination"] == "session" for u in d["updatedPermissions"])
    await dev.close()


async def test_approve_for_session_with_only_a_mode_suggestion_is_plain_allow(stack):
    from companion.core.state import Choice
    from companion.platforms.claude_code.attached import decision_output
    out = decision_output(Choice.APPROVE_SESSION, [{"type": "setMode", "mode": "acceptEdits"}])
    assert out["hookSpecificOutput"]["decision"] == {"behavior": "allow"}


async def _pending_approval(stack, ts=100.0):
    app, ws_url, hook_url = await stack()
    dev = await device(ws_url)
    pending = asyncio.create_task(post(hook_url, {**perm_request(), "_ts": ts}))
    await dev.wait_for(lambda d: d.view["screen"] == "approval")
    return app, dev, hook_url, pending


async def test_answering_in_the_terminal_clears_the_device(stack):
    app, dev, hook_url, pending = await _pending_approval(stack)
    req = perm_request()
    # you pressed Yes in Claude Code's own menu: the tool ran
    await post(hook_url, {**req, "hook_event_name": "PostToolUse", "tool_use_id": "t1", "tool_response": {},
                          "_ts": 101.0})
    assert await asyncio.wait_for(pending, 3) == {}  # our late answer is "no decision"
    await dev.wait_for(lambda d: d.view["screen"] == "home" and "Answered in the terminal" in d.toasts)
    await dev.close()


async def test_turn_ending_clears_the_device(stack):
    app, dev, hook_url, pending = await _pending_approval(stack)
    # you pressed No in Claude Code's menu and Claude finished its reply
    await post(hook_url, {"session_id": SID, "cwd": "/x", "hook_event_name": "Stop", "_ts": 102.0})
    assert await asyncio.wait_for(pending, 3) == {}
    await dev.wait_for(lambda d: d.view["screen"] == "home")
    await dev.close()


async def test_late_events_from_before_the_question_dont_clear_it(stack):
    app, dev, hook_url, pending = await _pending_approval(stack, ts=100.0)
    req = perm_request()
    # async hooks can arrive out of order: these fired before the PermissionRequest
    await post(hook_url, {**req, "hook_event_name": "PreToolUse", "tool_use_id": "t1", "_ts": 99.0})
    await post(hook_url, {"session_id": SID, "hook_event_name": "UserPromptSubmit", "prompt": "x", "_ts": 98.0})
    await asyncio.sleep(0.1)
    assert dev.view["screen"] == "approval" and not pending.done()
    # a different tool finishing doesn't count either (Claude can run tools in parallel)
    await post(hook_url, {**req, "hook_event_name": "PostToolUse", "tool_input": {"command": "ls"}, "_ts": 103.0})
    await asyncio.sleep(0.1)
    assert dev.view["screen"] == "approval"
    await dev.send_input("click")
    assert (await asyncio.wait_for(pending, 3))["hookSpecificOutput"]["decision"]["behavior"] == "allow"
    await dev.close()


async def test_late_status_event_does_not_overwrite_newer_status(stack):
    app, ws_url, hook_url = await stack()
    base = {"session_id": SID, "cwd": "/Users/nico/projects/alpha"}
    await post(hook_url, {**base, "hook_event_name": "Stop", "last_assistant_message": "done", "_ts": 200.0})
    await post(hook_url, {**base, "hook_event_name": "PreToolUse", "tool_name": "Bash",
                          "tool_input": {"command": "ls"}, "_ts": 199.0})  # arrived late
    assert app.state.sessions[SID].status.value == "done"
