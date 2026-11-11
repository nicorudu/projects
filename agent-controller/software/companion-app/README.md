# Companion app

Runs on the Mac (or Windows PC). It holds all the logic: it watches your AI agents, decides what the dock's screen shows, and turns key presses into actions. The dock and controller are thin clients.

How the code is organized: [docs/architecture.md](../../docs/architecture.md).

## Set up (once)

Needs Python 3.11 or newer (`python3 --version`; on a Mac, `brew install python@3.12` if it's older).

```bash
cd agent-controller/software/companion-app
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
python -m companion                 # the app; devices connect to ws://<this computer>:8765
python ../../tools/fake_device.py   # in a second terminal: the fake dock + controller
```

Fake device keys: arrow keys = stick, Enter = click, `c` Cancel, `v` Voice (press to hold, again to release), `s` Send, `q` quit.

## Test

```bash
python -m pytest -q
```

## Layout

| Folder | What's in it |
|---|---|
| `companion/core/` | state store, intents (what each key does on each screen), the app core |
| `companion/protocol/` | protocol v1 messages, audio frame header, COBS packet framing for USB |
| `companion/transports/` | Wi-Fi WebSocket (now), USB serial (M4) |
| `companion/devices/` | one connected device: outbox, heartbeat, duplicate-input check |
| `companion/view/` | builds the dock's screen from state and sends only what changed |
| `companion/platforms/` | plug-ins per AI tool (Claude Code first) |
| `companion/hooks/` | local HTTP server for Claude Code hooks |
| `main.py` | the original v0 (one Claude Code task over WebSocket); being folded into `platforms/claude_code/` |
