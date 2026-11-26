#!/usr/bin/env python3
"""Fake device: a terminal stand-in for the dock + controller, until the hardware arrives.

It speaks protocol v1 over the Wi-Fi path exactly like the real dock will, so the companion
app can't tell the difference.

    python tools/fake_device.py                 # connects to ws://localhost:8765
    python tools/fake_device.py --url ws://192.168.1.20:8765

Keys
    arrow keys          stick (one press = one flick): up/down select, right opens, left goes back
    c                   Cancel key
    s                   Send key (confirms an approval; brings a session's window forward)
    v                   Voice key (press once = hold down, again = release)
    g                   green button (home)
    q                   quit

The stick has no click, so Enter and space do nothing.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import textwrap
import time
from pathlib import Path

# Use the companion package from this repo even if it isn't pip-installed.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "software" / "companion-app"))

from websockets.asyncio.client import connect  # noqa: E402

from companion.protocol.messages import decode, encode, msg  # noqa: E402
from companion.view.builder import apply  # noqa: E402

FW = "fake-0.1"


class FakeDevice:
    """Async client. Used by the CLI below and by the end-to-end tests."""

    def __init__(self, url: str = "ws://localhost:8765", kind: str = "fake", heartbeat_s: float = 0.5):
        self.url = url
        self.kind = kind
        self.heartbeat_s = heartbeat_s
        self.ws = None
        self.view: dict | None = None
        self.led = "idle"
        self.toasts: list[str] = []
        self.sounds = 0
        self.acks: set[int] = set()
        self.seq = 0
        self.connected = False
        self._changed = asyncio.Condition()
        self._tasks: list[asyncio.Task] = []
        self._t0 = time.monotonic()

    def _ms(self) -> int:
        return int((time.monotonic() - self._t0) * 1000)

    async def connect(self) -> None:
        self.ws = await connect(self.url)
        await self.ws.send(encode(msg("hello", device=self.kind, fw=FW, transports=["wifi"],
                                      screen={"w": 480, "h": 320})))
        welcome = decode(await self.ws.recv())
        assert welcome["t"] == "welcome", welcome
        self.view = welcome.get("view")
        self.connected = True
        self._tasks = [asyncio.create_task(self._reader()), asyncio.create_task(self._heartbeat())]

    async def close(self) -> None:
        for t in self._tasks:
            t.cancel()
        if self.ws:
            await self.ws.close()
        self.connected = False

    def stop_heartbeat(self) -> None:
        """Tests: go silent without closing, like a device that lost Wi-Fi."""
        self._tasks[1].cancel()

    async def send_input(self, inp: str) -> int:
        self.seq += 1
        await self.ws.send(encode(msg("input", seq=self.seq, ts=self._ms(), **{"in": inp})))
        return self.seq

    async def _heartbeat(self) -> None:
        while True:
            await self.ws.send(encode(msg("ping", ts=self._ms())))
            await asyncio.sleep(self.heartbeat_s)

    async def _reader(self) -> None:
        try:
            async for raw in self.ws:
                m = decode(raw)
                t = m["t"]
                if t in ("view", "patch"):
                    self.view = apply(self.view, m)
                elif t == "led":
                    self.led = m["mode"]
                elif t == "toast":
                    self.toasts.append(m["text"])
                elif t == "sound":
                    self.sounds += 1
                elif t == "ack":
                    self.acks.add(m["seq"])
                async with self._changed:
                    self._changed.notify_all()
        finally:
            self.connected = False
            async with self._changed:
                self._changed.notify_all()

    async def wait_for(self, predicate, timeout: float = 3.0):
        """Wait until predicate(self) is true. Returns the device."""
        async def _wait():
            async with self._changed:
                await self._changed.wait_for(lambda: predicate(self))
        await asyncio.wait_for(_wait(), timeout)
        return self


# ---- terminal UI ---------------------------------------------------------------------
COLORS = {"working": "\033[34m", "waiting": "\033[33m", "done": "\033[32m", "error": "\033[31m",
          "ready": "\033[36m", "idle": "\033[90m", "recording": "\033[97m"}
DETAIL_COLS, DETAIL_LINES = 62, 10  # the detail page's text window
RESET, BOLD, DIM, REV = "\033[0m", "\033[1m", "\033[2m", "\033[7m"


def _ago(since: int) -> str:
    d = max(0, int(time.time()) - since)
    return f"{d}s" if d < 60 else f"{d // 60}m" if d < 3600 else f"{d // 3600}h"


def _dur(seconds: int) -> str:
    s = max(0, int(seconds))
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60}s"
    return f"{s // 3600}h {s % 3600 // 60}m"


def worked_line(v: dict, now: float | None = None) -> str:
    """The detail page's time line, like the reference's "Worked for 6m 24s"."""
    now = time.time() if now is None else now
    if v.get("turn_start") is not None:
        return f"Working for {_dur(now - v['turn_start'])}"
    if v.get("worked_s") is not None:
        return f"Worked for {_dur(v['worked_s'])}"
    return ""


def detail_window(text: str, scroll: int) -> tuple[list[str], int, int]:
    """Wrapped lines to show, the first line's number, and the total. Scroll stops at the end."""
    lines: list[str] = []
    for para in text.splitlines() or [""]:
        lines += textwrap.wrap(para, DETAIL_COLS) or [""]
    top = min(max(scroll, 0), max(len(lines) - DETAIL_LINES, 0))
    return lines[top:top + DETAIL_LINES], top, len(lines)


def render(dev: FakeDevice) -> str:
    v = dev.view or {}
    led = f"{COLORS.get(dev.led, '')}● {dev.led}{RESET}"
    lines = [f"{BOLD}AI Agent Controller — fake device{RESET}   LED {led}   "
             f"{'connected' if dev.connected else 'DISCONNECTED'}", "─" * 64]
    screen = v.get("screen")
    hdr = v.get("header", {})
    if screen == "home":
        lines.append(f"AGENTS   waiting {hdr.get('waiting', 0)} · working {hdr.get('working', 0)}")
        if not v["rows"]:
            lines.append(f"{DIM}  no sessions yet — start Claude Code in a terminal{RESET}")
        for i, r in enumerate(v["rows"]):
            mark = REV if i == v["sel"] else ""
            c = COLORS.get(r["status"], "")
            lines.append(f"{mark} {c}●{RESET}{mark} {c}{r['status'].upper():<8}{RESET}{mark} {r['name'][:22]:<22} "
                         f"{_ago(r['since']):>4}  {r['tool'][:24]} {RESET}")
    elif screen == "detail":
        c = COLORS.get(v["status"], "")
        shown, top, total = detail_window(v["text"], v["scroll"])
        lines += [f"{c}●{RESET} {BOLD}{v['name']}{RESET}  {c}{v['status'].upper()}{RESET}",
                  worked_line(v) or f"{DIM}({_ago(v['since'])} ago){RESET}",
                  f"{DIM}{v['cwd']}{RESET}"]
        if v["tool"]:
            lines.append(f"tool: {v['tool']}")
        lines += ["", *shown]
        if total > DETAIL_LINES:
            lines.append(f"{DIM}lines {top + 1}-{top + len(shown)} of {total}  (stick up/down scrolls){RESET}")
    elif screen == "approval":
        lines += [f"{COLORS['waiting']}{BOLD}APPROVAL{RESET}  {v['session']} wants to use "
                  f"{BOLD}{v['tool']}{RESET}   ({v['queue']} waiting)", "", f"  {v['summary']}", ""]
        for i, o in enumerate(v["options"]):
            lines.append(f"  {REV if i == v['sel'] else ''} {o} {RESET}")
    elif screen == "voice":
        lines.append(f"VOICE  {v.get('state')}")
    else:
        lines.append(str(v))
    lines += ["─" * 64, f"{DIM}stick: arrows (→ open, ← back) · c Cancel · s Send · v Voice · g green · q quit{RESET}"]
    if dev.toasts:
        lines.append(f"{BOLD}» {dev.toasts[-1]}{RESET}")
    return "\033[2J\033[H" + "\n".join(lines)


KEYMAP = {"\x1b[A": "up", "\x1b[B": "down", "\x1b[C": "right", "\x1b[D": "left",
          "c": "cancel", "s": "send", "g": "green"}


async def _keys():
    """Yields key strings. Raw mode on macOS/Linux; msvcrt on Windows."""
    if os.name == "nt":
        import msvcrt
        arrows = {"H": "\x1b[A", "P": "\x1b[B", "M": "\x1b[C", "K": "\x1b[D"}
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"):
                    yield arrows.get(msvcrt.getwch(), "")
                else:
                    yield ch
            else:
                await asyncio.sleep(0.02)
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        loop = asyncio.get_running_loop()
        q: asyncio.Queue = asyncio.Queue()
        loop.add_reader(fd, lambda: q.put_nowait(os.read(fd, 16).decode(errors="ignore")))
        try:
            while True:
                chunk = await q.get()
                while chunk:
                    if chunk.startswith("\x1b[") and len(chunk) >= 3:
                        yield chunk[:3]
                        chunk = chunk[3:]
                    else:
                        yield chunk[0]
                        chunk = chunk[1:]
        finally:
            loop.remove_reader(fd)
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


async def run_cli(url: str) -> None:
    dev = FakeDevice(url)
    try:
        await dev.connect()
    except OSError as e:
        print(f"Can't reach the companion app at {url} ({e}). Start it with: python -m companion")
        return
    voice_down = False

    async def redraw():
        while True:
            print(render(dev), end="", flush=True)
            async with dev._changed:
                try:
                    await asyncio.wait_for(dev._changed.wait(), 1.0)
                except asyncio.TimeoutError:
                    pass

    painter = asyncio.create_task(redraw())
    try:
        async for k in _keys():
            if k == "q":
                break
            if not dev.connected:
                continue
            if k == "v":
                voice_down = not voice_down
                await dev.send_input("voice_down" if voice_down else "voice_up")
            elif k in KEYMAP:
                await dev.send_input(KEYMAP[k])
    finally:
        painter.cancel()
        await dev.close()
        print("\nbye")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="ws://localhost:8765")
    args = ap.parse_args()
    try:
        asyncio.run(run_cli(args.url))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
