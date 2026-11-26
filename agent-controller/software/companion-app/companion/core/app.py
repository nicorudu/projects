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
from . import intents, names
from .state import APPROVAL_OPTIONS, IN_TURN, Approval, Choice, Screen, Session, State, Status

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
        self._follow_task: asyncio.Task | None = None  # pending "focus follows selection"
        self._repo_labels: dict[str, tuple[str, str]] = {}  # folder -> (repo name, top), so git runs once
        self._repo_lookups: dict[str, asyncio.Task] = {}

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
        if self._follow_task:
            self._tasks.append(self._follow_task)
        self._tasks += self._repo_lookups.values()
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
        elif t == "layout":
            self._on_layout(m)
        # "hello" after the handshake and "audio_end" are ignored until M2.

    def _on_layout(self, m: dict) -> None:
        """A screen device says how far the detail page it is showing can scroll."""
        f = self.state.focus
        if m.get("screen") != "detail" or f.screen != Screen.DETAIL or m.get("id") != f.detail_id:
            return  # about a page we've already left
        f.scroll_max = m["max_scroll"]
        if f.scroll > f.scroll_max:
            f.scroll = f.scroll_max
            self.mark_dirty()

    async def _watchdog(self) -> None:
        while True:
            await asyncio.sleep(min(0.25, self.cfg.heartbeat_timeout_s / 4))
            now = time.monotonic()
            for link in list(self.links.values()):
                if now - link.last_seen > self.cfg.heartbeat_timeout_s:
                    self.detach(link, "heartbeat timeout")
                    asyncio.create_task(link.close())
            self._age_sessions()

    def _age_sessions(self) -> None:
        """A finished or never-used session that has sat quiet long enough is shown as IDLE."""
        cutoff = time.time() - self.cfg.idle_after_s
        for s in self.state.sessions.values():
            if s.status in (Status.DONE, Status.READY) and s.since < cutoff:
                self._set_status(s, Status.IDLE)
                self.mark_dirty()

    # ---- sessions (called by platform plug-ins) -------------------------------
    def upsert_session(self, platform: str, sid: str, cwd: str | None = None, home: str | None = None,
                       touched: str | None = None, **changes) -> Session:
        """`cwd` is where the session is working now. `home` is where it was started, when the
        platform knows. `touched` is a file it is editing. The name comes from `home`'s repo and
        the top-level folder being worked in (core/names.py); a plain `cd` to the repo's top
        never renames a row."""
        s = self.state.sessions.get(sid)
        if s is None:
            s = Session(id=sid, platform=platform)
            self.state.sessions[sid] = s
        moved = bool(cwd) and cwd != s.cwd
        if moved:
            s.cwd = cwd
        if home:
            new_home, s.home_known = home, True
        else:  # not told: the first folder seen stands in, and later `cd`s don't change it
            new_home = cwd if not s.home else None
        if new_home and new_home != s.home:
            s.home, s.project = new_home, ""
            s.repo, s.repo_top = self._repo_labels.get(new_home, ("", ""))
            if new_home not in self._repo_labels:
                self._look_up_repo(new_home)
            self._note_work_folder(s, s.last_dir or s.cwd or new_home)
        if touched:  # the folder of a file being edited says more than the cwd
            self._note_work_folder(s, os.path.dirname(os.path.join(s.cwd, touched)))
        elif moved:
            self._note_work_folder(s, cwd)
        s.name = self._session_name(s)
        status = changes.pop("status", None)
        if status is not None:
            status = Status(status)
            # Don't let a status event hide an approval we're still holding.
            if any(a.session_id == sid for a in self.state.approvals) and status == Status.WORKING:
                status = Status.WAITING
            if self._set_status(s, status):
                if status == Status.WAITING and self.cfg.alert_sound:
                    self._broadcast(msg("sound", name="alert"))
        for k, v in changes.items():
            if v is not None:
                setattr(s, k, v)
        self.mark_dirty()
        return s

    def _set_status(self, s: Session, status: Status) -> bool:
        """Change a session's status and keep its turn timer. Returns False if nothing changed."""
        if status == s.status:
            return False
        now = time.time()
        if status in IN_TURN and s.status not in IN_TURN:
            s.turn_started = now  # a new turn begins
        elif status not in IN_TURN and s.status in IN_TURN:
            if s.turn_started is not None:
                s.worked_s = now - s.turn_started
            s.turn_started = None
        s.status, s.since = status, now
        return True

    def end_session(self, sid: str) -> None:
        f = self.state.focus
        if sid == f.sel_id:  # keep the highlight on the same row once the session is gone
            f.sel, f.sel_id = self.state.selected_index(), None
        if self.state.sessions.pop(sid, None) is not None:
            for a in [a for a in self.state.approvals if a.session_id == sid]:
                self._settle(a, None)
            if f.detail_id == sid and f.screen == Screen.DETAIL:
                f.screen = Screen.HOME
            self.mark_dirty()

    @staticmethod
    def _note_work_folder(s: Session, directory: str) -> None:
        """Remember where the session works. Inside one of the repo's top-level folders, that
        folder becomes the project and stays so until the session works in another one."""
        s.last_dir = directory
        sub = names.project_folder(s.repo_top, directory)
        if sub:
            s.project = sub

    @staticmethod
    def _project(s: Session) -> str:
        """The repo's folder being worked in, then the repo name, then the start folder's name."""
        return s.project or s.repo or (os.path.basename(s.home.rstrip("/\\")) if s.home else "") or s.id[:8]

    def _session_name(self, s: Session) -> str:
        base = self._project(s)
        clash = any(o.id != s.id and self._project(o) == base for o in self.state.sessions.values())
        return f"{base} ·{s.id[:4]}" if clash else base

    def _look_up_repo(self, cwd: str) -> None:
        """Ask git for the folder's repo name without holding up the event loop."""
        if cwd in self._repo_lookups:
            return
        try:
            self._repo_lookups[cwd] = asyncio.get_running_loop().create_task(self._repo_lookup(cwd))
        except RuntimeError:
            pass  # no loop (a plain unit test): the folder name is used

    async def _repo_lookup(self, cwd: str) -> None:
        try:
            info = await asyncio.to_thread(names.repo_info, cwd)
        except Exception:  # naming must never take the app down
            log.exception("repo lookup failed for %s", cwd)
            info = ("", "")
        self._repo_labels[cwd] = info
        self._repo_lookups.pop(cwd, None)
        if not info[0]:
            return
        for s in self.state.sessions.values():
            if s.home == cwd:
                s.repo, s.repo_top = info
                latest = s.last_dir
                self._note_work_folder(s, s.home)  # started inside a project folder
                if latest:
                    self._note_work_folder(s, latest)  # and where it has worked since
        for s in self.state.sessions.values():
            s.name = self._session_name(s)
        self.mark_dirty()

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
        if s:
            self._set_status(s, Status.WAITING)
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
                self._set_status(s, Status.WORKING)
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

    def _move_sel(self, step: int) -> None:
        rows = self.state.visible_sessions()
        if not rows:
            return
        f = self.state.focus
        old = self.state.selected_index(rows)
        new = min(len(rows) - 1, max(0, old + step))
        f.sel, f.sel_id = new, rows[new].id
        if new != old and self.cfg.focus_follows_selection:
            self._follow_selection(rows[new].id)

    def _do_sel_prev(self):
        self._move_sel(-1)

    def _do_sel_next(self):
        self._move_sel(1)

    def _follow_selection(self, sid: str) -> None:
        """Bring the selected session's window forward once the stick has rested on it."""
        self._cancel_follow()
        self._follow_task = asyncio.create_task(self._follow_after_delay(sid), name="follow")

    def _cancel_follow(self) -> None:
        if self._follow_task and not self._follow_task.done():
            self._follow_task.cancel()
        self._follow_task = None

    async def _follow_after_delay(self, sid: str) -> None:
        await asyncio.sleep(self.cfg.focus_follow_delay_s)
        s = self.state.selected_session()
        if self.state.focus.screen != Screen.HOME or s is None or s.id != sid:
            return  # the selection moved on, or another screen took over
        p = self.platforms.get(s.platform)
        if p is None or not hasattr(p, "focus"):
            return
        try:
            await p.focus(sid, quiet=True)
        except Exception:  # a focus failure must never take the app down
            log.exception("focus follows selection failed for %s", sid)

    def _do_open_detail(self):
        s = self.state.selected_session()
        if s:
            f = self.state.focus
            f.screen, f.detail_id, f.scroll, f.scroll_max = Screen.DETAIL, s.id, 0, None
            f.sel_id = s.id  # going back lands on the same row

    def _do_go_home(self):
        self.state.focus.screen = Screen.HOME

    def _do_scroll_up(self):
        self.state.focus.scroll = max(0, self.state.focus.scroll - 1)

    def _do_scroll_down(self):
        f = self.state.focus
        if f.scroll_max is None or f.scroll < f.scroll_max:  # stop at the end once the device said where it is
            f.scroll += 1

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
        self._cancel_follow()  # Send means "now"; don't focus a second time
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
