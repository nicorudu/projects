"""The companion app's core: owns the state, reacts to devices and platforms, renders views.

Single asyncio loop. Reducers here are the only code that changes State. After any change,
`mark_dirty()` wakes the render loop, which sends each screen device the smallest update.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time

from ..config import Config
from ..devices.link import DeviceLink
from ..protocol.messages import ProtocolError, msg, validate_from_device
from ..view import builder
from . import intents
from .state import APPROVAL_OPTIONS, HOME_FILTERS, Approval, Choice, Screen, Session, State, Status

log = logging.getLogger(__name__)

_CHOICE_TOAST = {
    Choice.APPROVE: "Approved",
    Choice.APPROVE_SESSION: "Approved for session",
    Choice.REJECT: "Rejected",
    Choice.ASK_TERMINAL: "Answer in the terminal",
}


class App:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.state = State()
        self.links: dict[str, DeviceLink] = {}
        self.platforms: dict = {}
        self._dirty = asyncio.Event()
        self._tasks: list[asyncio.Task] = []

    # ---- lifecycle -----------------------------------------------------------
    async def start(self) -> None:
        self._tasks += [
            asyncio.create_task(self._render_loop(), name="render"),
            asyncio.create_task(self._watchdog(), name="watchdog"),
        ]
        for p in self.platforms.values():
            await p.start(self)

    async def stop(self) -> None:
        for a in list(self.state.approvals):
            self._settle(a, None)
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        for link in list(self.links.values()):
            await link.close()

    def register_platform(self, platform) -> None:
        self.platforms[platform.name] = platform

    # ---- devices -------------------------------------------------------------
    def attach(self, link: DeviceLink) -> None:
        self.links[link.id] = link
        view = builder.build(self.state) if link.has_screen else None
        link.send(msg("welcome", proto=1, mac_ms=int(time.time() * 1000), view=view))
        link.last_view = view
        if link.has_screen:
            link.last_led = builder.led_mode(self.state)
            link.send(msg("led", mode=link.last_led))
        log.info("device connected: %s (fw %s, %s)", link.id, link.fw, link.conn.path)
        self.mark_dirty()

    def detach(self, link: DeviceLink, reason: str = "closed") -> None:
        if self.links.pop(link.id, None) is None:
            return
        link.closed = True
        log.info("device disconnected: %s (%s)", link.id, reason)
        if not self.has_input_device:
            # Nobody can press a key now: hand every waiting approval back to Claude Code's prompt.
            for a in list(self.state.approvals):
                self._settle(a, None)
        self.mark_dirty()

    @property
    def has_input_device(self) -> bool:
        return any(l.has_input for l in self.links.values())

    def on_device_message(self, link: DeviceLink, m: dict) -> None:
        link.last_seen = time.monotonic()
        try:
            validate_from_device(m)
        except ProtocolError as e:
            log.warning("bad message from %s: %s", link.id, e)
            return
        t = m["t"]
        if t == "ping":
            link.send(msg("pong", ts=m.get("ts")))
        elif t == "input":
            link.send(msg("ack", seq=m["seq"]))
            if not link.is_duplicate(m["seq"]):
                self.handle_input(m["in"])
        # "hello" after the handshake and "audio_end" are ignored until M2.

    async def _watchdog(self) -> None:
        while True:
            await asyncio.sleep(min(0.25, self.cfg.heartbeat_timeout_s / 4))
            now = time.monotonic()
            for link in list(self.links.values()):
                if now - link.last_seen > self.cfg.heartbeat_timeout_s:
                    self.detach(link, "heartbeat timeout")
                    asyncio.create_task(link.close())

    # ---- sessions (called by platform plug-ins) -------------------------------
    def upsert_session(self, platform: str, sid: str, cwd: str | None = None, **changes) -> Session:
        s = self.state.sessions.get(sid)
        if s is None:
            s = Session(id=sid, platform=platform)
            self.state.sessions[sid] = s
        if cwd and cwd != s.cwd:
            s.cwd = cwd
        s.name = self._session_name(s)
        status = changes.pop("status", None)
        if status is not None:
            status = Status(status)
            # Don't let a status event hide an approval we're still holding.
            if any(a.session_id == sid for a in self.state.approvals) and status == Status.WORKING:
                status = Status.WAITING
            if status != s.status:
                s.status = status
                s.since = time.time()
                if status == Status.WAITING and self.cfg.alert_sound:
                    self._broadcast(msg("sound", name="alert"))
        for k, v in changes.items():
            if v is not None:
                setattr(s, k, v)
        self.mark_dirty()
        return s

    def end_session(self, sid: str) -> None:
        if self.state.sessions.pop(sid, None) is not None:
            for a in [a for a in self.state.approvals if a.session_id == sid]:
                self._settle(a, None)
            f = self.state.focus
            if f.detail_id == sid and f.screen == Screen.DETAIL:
                f.screen = Screen.HOME
            self.mark_dirty()

    def _session_name(self, s: Session) -> str:
        base = os.path.basename(s.cwd.rstrip("/\\")) if s.cwd else ""
        base = base or s.id[:8]
        clash = any(o.id != s.id and o.cwd and os.path.basename(o.cwd.rstrip("/\\")) == base
                    for o in self.state.sessions.values())
        return f"{base} ·{s.id[:4]}" if clash else base

    # ---- approvals -------------------------------------------------------------
    def add_approval(self, a: Approval) -> None:
        q = self.state.approvals
        q.append(a)
        f = self.state.focus
        if f.screen != Screen.APPROVAL:
            f.return_to = f.screen
            f.screen = Screen.APPROVAL
            f.approval_sel = 0
        s = self.state.sessions.get(a.session_id)
        if s and s.status != Status.WAITING:
            s.status, s.since = Status.WAITING, time.time()
        if self.cfg.alert_sound:
            self._broadcast(msg("sound", name="alert"))
        self.mark_dirty()

    def _settle(self, a: Approval, choice: Choice | None) -> None:
        """Answer an approval (None = no decision) and take it off the queue."""
        if not a.future.done():
            a.future.set_result(choice)
        if a in self.state.approvals:
            self.state.approvals.remove(a)
        f = self.state.focus
        if not self.state.approvals and f.screen == Screen.APPROVAL:
            f.screen = f.return_to if f.return_to != Screen.APPROVAL else Screen.HOME
        f.approval_sel = 0
        s = self.state.sessions.get(a.session_id)
        if s and not any(x.session_id == s.id for x in self.state.approvals):
            if choice in (Choice.APPROVE, Choice.APPROVE_SESSION, Choice.REJECT):
                s.status, s.since = Status.WORKING, time.time()
        self.mark_dirty()

    def withdraw_approval(self, a: Approval) -> None:
        """The hook gave up waiting (timeout or Claude Code hung up)."""
        if a in self.state.approvals:
            self._settle(a, None)

    # ---- inputs ----------------------------------------------------------------
    def handle_input(self, inp: str) -> None:
        f = self.state.focus
        action = intents.resolve(f.screen, inp)
        log.debug("input %s on %s -> %s", inp, f.screen.value, action)
        if action:
            getattr(self, f"_do_{action}")()
            self.mark_dirty()

    def _do_sel_prev(self):
        self.state.focus.sel = max(0, self.state.focus.sel - 1)

    def _do_sel_next(self):
        n = len(self.state.visible_sessions())
        self.state.focus.sel = min(max(n - 1, 0), self.state.focus.sel + 1)

    def _cycle_filter(self, step):
        f = self.state.focus
        f.filter = HOME_FILTERS[(HOME_FILTERS.index(f.filter) + step) % len(HOME_FILTERS)]
        f.sel = 0

    def _do_filter_prev(self):
        self._cycle_filter(-1)

    def _do_filter_next(self):
        self._cycle_filter(1)

    def _do_open_detail(self):
        s = self.state.selected_session()
        if s:
            f = self.state.focus
            f.screen, f.detail_id, f.scroll = Screen.DETAIL, s.id, 0

    def _do_go_home(self):
        self.state.focus.screen = Screen.HOME

    def _do_scroll_up(self):
        self.state.focus.scroll = max(0, self.state.focus.scroll - 1)

    def _do_scroll_down(self):
        self.state.focus.scroll += 1

    def _detail_step(self, step):
        ids = [s.id for s in self.state.visible_sessions()] or list(self.state.sessions)
        f = self.state.focus
        if not ids:
            return
        i = ids.index(f.detail_id) if f.detail_id in ids else 0
        f.detail_id, f.scroll = ids[(i + step) % len(ids)], 0

    def _do_detail_prev(self):
        self._detail_step(-1)

    def _do_detail_next(self):
        self._detail_step(1)

    def _do_option_prev(self):
        self.state.focus.approval_sel = (self.state.focus.approval_sel - 1) % len(APPROVAL_OPTIONS)

    def _do_option_next(self):
        self.state.focus.approval_sel = (self.state.focus.approval_sel + 1) % len(APPROVAL_OPTIONS)

    def _do_confirm_option(self):
        if self.state.approvals:
            choice, _ = APPROVAL_OPTIONS[self.state.focus.approval_sel]
            self._settle(self.state.approvals[0], choice)
            self.toast(_CHOICE_TOAST[choice])

    def _do_reject(self):
        if self.state.approvals:
            self._settle(self.state.approvals[0], Choice.REJECT)
            self.toast("Rejected")

    def _do_focus_session(self):
        f = self.state.focus
        s = self.state.sessions.get(f.detail_id) if f.screen == Screen.DETAIL else self.state.selected_session()
        if not s:
            return
        p = self.platforms.get(s.platform)
        if p is None or not hasattr(p, "focus"):
            self.toast("Can't open that one")
            return
        self.toast(f"Opening {s.name}")
        asyncio.create_task(p.focus(s.id))

    # Voice arrives in M2; keep the keys harmless until then.
    def _do_voice_start(self):
        self.toast("Voice arrives in M2")

    def _do_voice_stop(self):
        pass

    def _do_voice_discard(self):
        self.state.focus.screen = Screen.HOME

    def _do_voice_deliver(self):
        self.state.focus.screen = Screen.HOME

    # ---- output ----------------------------------------------------------------
    def toast(self, text: str, ms: int = 1500) -> None:
        self._broadcast(msg("toast", text=text, ms=ms))

    def _broadcast(self, m: dict) -> None:
        for link in self.links.values():
            if link.has_screen:
                link.send(m)

    def mark_dirty(self) -> None:
        self._dirty.set()

    async def _render_loop(self) -> None:
        while True:
            await self._dirty.wait()
            self._dirty.clear()
            self.render_now()
            await asyncio.sleep(0)  # let a burst of events coalesce into one update

    def render_now(self) -> None:
        view = builder.build(self.state)
        led = builder.led_mode(self.state)
        for link in self.links.values():
            if not link.has_screen:
                continue
            m = builder.diff(link.last_view, view)
            if m is not None:
                link.send(m)
                link.last_view = view
            if led != link.last_led:
                link.send(msg("led", mode=led))
                link.last_led = led
