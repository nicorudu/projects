"""Path A: Wi-Fi WebSocket. The dock (and the fake device) connect to ws://<mac>:8765.

JSON goes in text frames, audio in binary frames (M2).
"""

from __future__ import annotations

import asyncio
import logging

from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed

from ..devices.link import DeviceLink
from ..protocol.messages import ProtocolError, decode, validate_from_device

log = logging.getLogger(__name__)


class _WsConnection:
    path = "wifi"

    def __init__(self, ws: ServerConnection):
        self.ws = ws

    async def send_text(self, text: str) -> None:
        await self.ws.send(text)

    async def send_bytes(self, data: bytes) -> None:
        await self.ws.send(data)

    async def close(self) -> None:
        await self.ws.close()


class WebSocketTransport:
    def __init__(self, app, host: str, port: int):
        self.app = app
        self.host = host
        self.port = port
        self._server = None

    async def start(self) -> None:
        self._server = await serve(self._handle, self.host, self.port, ping_interval=None, max_size=2**20)
        self.port = self._server.sockets[0].getsockname()[1]  # real port when 0 was asked for
        log.info("device link listening on ws://%s:%d", self.host, self.port)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handle(self, ws: ServerConnection) -> None:
        conn = _WsConnection(ws)
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=self.app.cfg.hello_timeout_s)
            hello = validate_from_device(decode(raw))
            if hello["t"] != "hello":
                raise ProtocolError("first message must be hello")
        except (asyncio.TimeoutError, ProtocolError, ConnectionClosed) as e:
            log.warning("rejected device from %s: %s", ws.remote_address, e)
            await ws.close(code=1002, reason="hello required")
            return

        link = DeviceLink(conn, hello)
        writer = asyncio.create_task(link.writer())
        self.app.attach(link)
        try:
            async for raw in ws:
                if isinstance(raw, bytes):
                    continue  # audio frames: M2
                try:
                    self.app.on_device_message(link, decode(raw))
                except ProtocolError as e:
                    log.warning("bad message from %s: %s", link.id, e)
        except ConnectionClosed:
            pass
        finally:
            self.app.detach(link)
            # let queued messages drain briefly, then stop the writer
            await asyncio.sleep(0)
            writer.cancel()
