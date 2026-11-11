"""Path B: the dock's native USB (CDC serial). Built in M4, when the dock exists.

Plan: open the port with pyserial-asyncio, feed bytes into protocol.framing.PacketReader,
send with protocol.framing.pack(KIND_JSON, encode(msg).encode()). Everything above the
Connection interface (handshake, heartbeat, views) is shared with the WebSocket path.
"""

from __future__ import annotations


class SerialTransport:  # pragma: no cover - placeholder until M4
    path = "usb"

    def __init__(self, *_, **__):
        raise NotImplementedError("USB serial transport arrives in M4 (needs the dock hardware)")
