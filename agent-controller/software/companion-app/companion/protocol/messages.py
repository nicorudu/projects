"""Protocol v1 messages (mirrors firmware/lib/protocol/messages.h, written in M3/M4).

Every JSON message is an object with "v": 1 and a type "t".

Device -> Mac
  hello   {device: "dock"|"controller"|"fake", fw, transports: [...], screen: {w, h} | null}
  ping    {ts}
  input   {seq, ts, in: one of INPUTS}            (acked by the Mac with "ack")
  audio_end {stream_id}                           (M2)

Mac -> Device
  welcome {proto, mac_ms, view}                   full current screen
  pong    {ts}                                    echoes the ping's ts
  ack     {seq}
  view    {screen, ...data}                       replace the whole screen
  patch   {screen, set: {key: value}}             change some fields of the current screen
  led     {mode: idle|working|waiting|done|error|recording}
  sound   {name: "alert"}
  toast   {text, ms}

Flick detection happens on the controller, so the Mac only ever sees directions.
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass

VERSION = 1

INPUTS = frozenset(
    {"up", "down", "left", "right", "click", "cancel", "voice_down", "voice_up", "send"}
)
DEVICE_TYPES = frozenset({"dock", "controller", "fake"})
DEVICE_TO_MAC = frozenset({"hello", "ping", "input", "audio_end"})
MAC_TO_DEVICE = frozenset({"welcome", "pong", "ack", "view", "patch", "led", "sound", "toast"})
LED_MODES = frozenset({"idle", "working", "waiting", "done", "error", "recording"})


class ProtocolError(ValueError):
    pass


def msg(t: str, **fields) -> dict:
    return {"v": VERSION, "t": t, **fields}


def encode(m: dict) -> str:
    return json.dumps(m, separators=(",", ":"), ensure_ascii=False)


def decode(text: str | bytes) -> dict:
    try:
        m = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ProtocolError(f"not JSON: {e}") from None
    if not isinstance(m, dict):
        raise ProtocolError("message must be a JSON object")
    if m.get("v") != VERSION:
        raise ProtocolError(f"unsupported protocol version {m.get('v')!r}")
    if not isinstance(m.get("t"), str):
        raise ProtocolError("missing type 't'")
    return m


def validate_from_device(m: dict) -> dict:
    """Checks the fields the Mac relies on. Raises ProtocolError."""
    t = m["t"]
    if t not in DEVICE_TO_MAC:
        raise ProtocolError(f"unknown device message type {t!r}")
    if t == "hello":
        if m.get("device") not in DEVICE_TYPES:
            raise ProtocolError(f"unknown device {m.get('device')!r}")
    elif t == "input":
        if m.get("in") not in INPUTS:
            raise ProtocolError(f"unknown input {m.get('in')!r}")
        if not isinstance(m.get("seq"), int):
            raise ProtocolError("input needs an integer seq")
    return m


# ---- audio frames (binary) -------------------------------------------------
# Header: stream_id:u8, seq:u16, codec:u8, samples:u16 (little-endian), then data.
AUDIO_HEADER = struct.Struct("<BHBH")
CODEC_PCM16 = 0
CODEC_IMA_ADPCM = 1
SAMPLE_RATE = 16_000


@dataclass(frozen=True)
class AudioFrame:
    stream_id: int
    seq: int
    codec: int
    samples: int
    data: bytes

    def pack(self) -> bytes:
        return AUDIO_HEADER.pack(self.stream_id, self.seq & 0xFFFF, self.codec, self.samples) + self.data

    @classmethod
    def unpack(cls, raw: bytes) -> "AudioFrame":
        if len(raw) < AUDIO_HEADER.size:
            raise ProtocolError("audio frame shorter than its header")
        sid, seq, codec, samples = AUDIO_HEADER.unpack_from(raw)
        return cls(sid, seq, codec, samples, bytes(raw[AUDIO_HEADER.size:]))
