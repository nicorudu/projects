import os

import pytest

from companion.protocol import framing
from companion.protocol.messages import (AudioFrame, ProtocolError, decode, encode, msg,
                                         validate_from_device)


def test_roundtrip():
    m = msg("input", seq=3, ts=10, **{"in": "up"})
    assert decode(encode(m)) == m == {"v": 1, "t": "input", "seq": 3, "ts": 10, "in": "up"}


@pytest.mark.parametrize("raw", ['{"t":"ping"}', '{"v":2,"t":"ping"}', "[1]", "nope", '{"v":1}'])
def test_decode_rejects(raw):
    with pytest.raises(ProtocolError):
        decode(raw)


def test_validate():
    validate_from_device(msg("hello", device="dock"))
    with pytest.raises(ProtocolError):
        validate_from_device(msg("hello", device="toaster"))
    with pytest.raises(ProtocolError):
        validate_from_device(msg("input", seq=1, **{"in": "jump"}))
    with pytest.raises(ProtocolError):
        validate_from_device(msg("input", **{"in": "up"}))  # no seq
    with pytest.raises(ProtocolError):
        validate_from_device(msg("view", screen="home"))  # Mac->device type


def test_audio_frame():
    f = AudioFrame(stream_id=2, seq=70000, codec=1, samples=320, data=b"\x01\x02")
    raw = f.pack()
    assert len(raw) == 6 + 2
    g = AudioFrame.unpack(raw)
    assert (g.stream_id, g.seq, g.codec, g.samples, g.data) == (2, 70000 & 0xFFFF, 1, 320, b"\x01\x02")
    with pytest.raises(ProtocolError):
        AudioFrame.unpack(b"\x00\x01")


@pytest.mark.parametrize("data", [b"", b"\x00", b"\x00\x00", b"\x11\x22\x00\x33", bytes(range(1, 255)),
                                  bytes(range(1, 256)) * 3, b"\x01" * 254 + b"\x00", os.urandom(1000)])
def test_cobs_roundtrip(data):
    enc = framing.cobs_encode(data)
    assert 0 not in enc
    assert framing.cobs_decode(enc) == data


def test_packet_reader_split_and_garbage():
    p1 = framing.pack(framing.KIND_JSON, encode(msg("ping", ts=1)).encode())
    p2 = framing.pack(framing.KIND_AUDIO, b"\x00\x01\x02\x00")
    stream = b"\x05\x00" + p1 + p2  # a broken packet first, then two good ones
    r = framing.PacketReader()
    got = []
    for i in range(0, len(stream), 3):  # arrive in small chunks
        got += r.feed(stream[i:i + 3])
    assert got == [(1, encode(msg("ping", ts=1)).encode()), (2, b"\x00\x01\x02\x00")]
    assert r.errors == 1
