"""One connected device (dock, controller, or the fake device), whatever transport it uses."""

from __future__ import annotations

import asyncio
import itertools
import logging
import time

from ..protocol.messages import encode

log = logging.getLogger(__name__)
_ids = itertools.count(1)


class DeviceLink:
    def __init__(self, conn, hello: dict):
        self.conn = conn
        self.id = f"{hello['device']}-{next(_ids)}"
        self.kind: str = hello["device"]
        self.fw: str = str(hello.get("fw", "?"))
        self.has_screen = self.kind in ("dock", "fake")
        self.has_input = self.kind in ("dock", "controller", "fake")
        self.last_seen = time.monotonic()
        self.last_seq: int | None = None
        self.last_view: dict | None = None  # what this device is showing now
        self.last_led: str | None = None
        self.outbox: asyncio.Queue = asyncio.Queue()
        self.closed = False

    def send(self, m: dict) -> None:
        """Queue a message. One writer per link keeps the order."""
        if not self.closed:
            self.outbox.put_nowait(m)

    async def writer(self) -> None:
        while True:
            m = await self.outbox.get()
            try:
                await self.conn.send_text(encode(m))
            except Exception as e:  # connection gone; the reader side will clean up
                log.debug("send to %s failed: %s", self.id, e)
                return

    def is_duplicate(self, seq: int) -> bool:
        """Inputs are acked; a resent input (same seq) must not act twice."""
        if self.last_seq is not None and seq == self.last_seq:
            return True
        self.last_seq = seq
        return False

    async def close(self) -> None:
        self.closed = True
        try:
            await self.conn.close()
        except Exception:
            pass
