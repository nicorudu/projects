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

Fake device keys (the reference's controls, since M1b):

| Key | Control | What it does |
|---|---|---|
| ↑ / ↓ | Stick | Select a session (its window comes forward after 0.6 s), scroll, or change the approval option |
| → | Stick | Open the selected session's detail page |
| ← | Stick | Back |
| `s` | Send | Confirm an approval; bring the session's window forward now |
| `c` | Cancel | Reject an approval; back |
| `v` | Voice | Press to hold, again to release (M2) |
| `g` | Green button | Home |
| `q` | — | Quit |

The stick has no click, so Enter does nothing. Only Send confirms an approval.

Settings in `~/.agent-controller/config.toml`: `focus_follows_selection = false` stops windows coming forward as you move the selection; `focus_follow_delay_s` (0.6) and `idle_after_s` (600) set the two timings.

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
