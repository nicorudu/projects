"""Packet framing for USB serial (Path B) and ESP-NOW.

A packet is [kind:u8][payload]; kind 1 = JSON text, 2 = audio frame.
On the serial line each packet is COBS-encoded and ends with a 0x00 byte, so a
receiver can always find the next packet boundary even after garbage.
WebSocket (Path A) doesn't need this: text frames carry JSON, binary frames carry audio.
"""

from __future__ import annotations

KIND_JSON = 1
KIND_AUDIO = 2
ESPNOW_MAX = 250


class FramingError(ValueError):
    pass


def cobs_encode(data: bytes) -> bytes:
    out = bytearray()
    block = bytearray()
    for byte in data:
        if byte == 0:
            out.append(len(block) + 1)
            out += block
            block.clear()
        else:
            block.append(byte)
            if len(block) == 254:
                out.append(255)
                out += block
                block.clear()
    out.append(len(block) + 1)
    out += block
    return bytes(out)


def cobs_decode(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        code = data[i]
        if code == 0:
            raise FramingError("zero byte inside COBS data")
        i += 1
        end = i + code - 1
        if end > n:
            raise FramingError("COBS block runs past the end")
        block = data[i:end]
        if 0 in block:
            raise FramingError("zero byte inside COBS data")
        out += block
        i = end
        if code != 255 and i < n:
            out.append(0)
    return bytes(out)


def pack(kind: int, payload: bytes) -> bytes:
    """One serial packet, ready to write: COBS([kind] + payload) + 0x00."""
    return cobs_encode(bytes([kind]) + payload) + b"\x00"


class PacketReader:
    """Feed it raw serial bytes; it returns complete (kind, payload) packets."""

    def __init__(self, max_len: int = 64 * 1024):
        self._buf = bytearray()
        self._max = max_len
        self.errors = 0

    def feed(self, chunk: bytes) -> list[tuple[int, bytes]]:
        packets = []
        self._buf += chunk
        while True:
            idx = self._buf.find(0)
            if idx < 0:
                if len(self._buf) > self._max:  # no delimiter for too long: drop and resync
                    self._buf.clear()
                    self.errors += 1
                break
            raw = bytes(self._buf[:idx])
            del self._buf[: idx + 1]
            if not raw:
                continue
            try:
                decoded = cobs_decode(raw)
            except FramingError:
                self.errors += 1
                continue
            if decoded:
                packets.append((decoded[0], decoded[1:]))
        return packets
