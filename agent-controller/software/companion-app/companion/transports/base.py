"""What a transport has to provide. Each connected device gets one Connection.

Path A (Wi-Fi WebSocket) is in websocket.py. Path B (USB serial with COBS packets)
goes in serial_usb.py once the dock exists (M4); the framing it needs is already in
protocol/framing.py and tested.
"""

from __future__ import annotations

from typing import Protocol


class Connection(Protocol):
    path: str  # "wifi" | "usb" | "espnow"

    async def send_text(self, text: str) -> None: ...
    async def send_bytes(self, data: bytes) -> None: ...
    async def close(self) -> None: ...
