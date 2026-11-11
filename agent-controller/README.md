# Projects

A monorepo of hardware and software builds by Nico.

## agent-controller

A physical AI agent controller (inspired by SlashVibe): a desk dock with a 4" screen and a detachable controller with keys, a thumbstick and mics. A Python companion app on the computer bridges it to Claude Code and other AI tools over USB or Wi-Fi.

### Status
- Companion app: working (v0)
- Hardware: parts on order (design rev 2: dock + detachable controller)
- Firmware: not started
- Voice pipeline and platform plug-ins: planned (see blueprint)

### Files
- `main.py` — Python companion app (WebSocket server + Claude Code subprocess)
- `docs/agent-controller-v0-blueprint.md` — rev 2: parts, pin maps, USB + Wi-Fi architecture, voice pipeline, platform plug-ins, build and test plan
- `docs/agent-controller-v0-spec.md` — original clamshell spec (superseded)
