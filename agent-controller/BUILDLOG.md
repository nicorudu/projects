# Build log — AI Agent Controller

Newest first. Each entry covers what changed, why, and links to its renders and docs.

---

## 2026-11-11 — Fixes from the Mac Mini test
- **Silent when the app is off.** Every Claude Code hook now runs a small script instead of Claude Code's built-in web hook. When the companion app isn't running, nothing shows in Claude Code. Checked live: 0 error lines.
- **Answer in either place.** Claude Code shows its own permission menu at the same time as the device. If you answer in the terminal, the device now clears the question as soon as the session moves on, instead of 2 minutes later.
- **"Approve for session" never changes Claude Code's mode.** It only adds the permission rule, for this session only.
- Status updates run in the background, so Claude Code never waits for the companion app. Late arrivals are put back in order.
- 54 automated tests.

## 2026-11-11 — M1 tested on the Mac Mini
- Ran the full Mac Mini test with a real Claude Code session, the companion app and the fake device in three Terminal windows.
- **Works:** live status and LED; Approve (Claude Code's own menu closes by itself and shows "Allowed by PermissionRequest hook"); Reject (Claude doesn't retry); Ask in terminal (the normal prompt answers as usual); Send brings the session's window to the front with no macOS permission prompt; a direct curl to the hook server.
- **Three issues found** (being fixed in a separate session):
  1. "Approve for session" also switched Claude Code to "accept edits on", because it applied every suggestion Claude Code offered, including a mode change.
  2. In interactive mode Claude Code shows its own permission menu while our hook waits, and the first answer wins. Answering in the terminal leaves a stale Approval screen on the device for 2 minutes.
  3. With the companion app off, Claude Code still works but prints `hook error: connect ECONNREFUSED 127.0.0.1:8766` on most events.
- Fixed a test that failed every time on the M4: it checked the LED a moment before the device had received it.

## 2026-11-11 — M1: Claude Code approvals from the device
- **First live approval.** A real Claude Code session asked for permission to run a Bash command. The fake device showed the Approval screen, one press of Approve let it run, and the command wrote its file.
- Claude Code status flows in through its hooks: working (with the current tool), waiting, done, error. The app sends them to a local hook server on `127.0.0.1:8766`.
- Approvals use the `PermissionRequest` hook. The options are Approve / Approve for session / Reject / Ask in terminal. If the device is off, you don't answer within 120 s, or Claude Code hangs up, it falls back to the normal terminal prompt.
- `python -m companion install-hooks` / `uninstall-hooks` edit `~/.claude/settings.json`. They back the file up first and never touch your other hooks. `doctor` checks the setup.
- Send on Home/Detail brings that session's terminal tab to the front (macOS: Terminal and iTerm2 by tab, other apps by name). Not tested on the Mac yet.
- The v0 `main.py` became `platforms/claude_code/managed.py`, and it no longer skips permissions.
- 45 automated tests, including every approval path end to end.

## 2026-11-11 — M0: companion app restructure + fake device
- The companion app is now a proper package (`software/companion-app/companion/`). It has protocol v1, a Wi-Fi WebSocket transport, the state store, the key map for every screen, and a view builder that sends the dock only what changed.
- USB packet framing (COBS) is written and tested now, so Path B only needs the serial port code when the dock arrives.
- `tools/fake_device.py` is a terminal stand-in for the dock + controller. It speaks the same protocol the real hardware will: arrow keys = stick, `c` / `v` / `s` = Cancel / Voice / Send.
- 28 automated tests cover the protocol, framing, screens, the handshake, heartbeat timeout, and duplicate-press protection.
- Added [HANDOFF.md](HANDOFF.md), updated after every step, so the plan survives any chat reset.

## 2026-11-11 — Code architecture
- Wrote the [software architecture](docs/architecture.md): three programs (companion app, dock firmware, controller firmware), one protocol over USB, Wi-Fi and ESP-NOW, screen-by-screen button map, voice pipeline, and platform plug-in contract.
- Claude Code approvals will use its HTTP `PermissionRequest` hook. The companion app holds the request until you press a key; if the device is off, Claude Code falls back to its normal prompt.
- Build order puts four milestones (fake device, Claude Code plug-in, voice on the Mac mic, UI simulator) before any hardware arrives.

## 2026-11-11 — Rev 2 locked: dock + detachable controller
- Studied SlashVibe's live Kickstarter: its controller is one rigid bar (3 keys and a stick at one end) that charges through magnetic contacts on the dock. We copied that layout. → [research notes](docs/research/slashvibe-reference.md)
- Added a **USB data path** (dock native USB, controller → dock over ESP-NOW) next to Wi-Fi. Both get built and timed head to head.
- Planned our own voice pipeline: local Whisper on the M4, Claude cleanup, a personal dictionary, Send/Cancel.
- Planned platform plug-ins: Claude Code first (hooks for status and approvals), then Cursor, the chat apps, and the cloud agents.
- Fixed the rev 1 pin map: I2S was on GPIO35–37, which the N16R8's octal PSRAM uses.
- Organized the repo as a physical-product project: a [BOM](hardware/bom/BOM.csv) with order status, a [decision log](docs/decisions.md), and folders for wiring, printing, firmware, tests and web images.
- Concept model and renders of rev 2, with no part collisions. → [renders](hardware/renders/2026-11-11-rev2-dock-controller/) · [CAD script](hardware/cad/rev2-dock-controller/concept.py) · [blueprint rev 2](docs/agent-controller-v0-blueprint.md)

![rev 2 exploded controller](media/web/rev2-05-exploded-controller.webp)

## 2026-11-09 — Rev 1 clamshell shell, then the pivot
- Wrote a parametric CadQuery clamshell. It checks fit automatically: part overlaps, how far the lid swings (137°), and joystick tilt clearance. → [renders](hardware/renders/2026-11-09-rev1-clamshell/) · [CAD script](hardware/cad/rev1-clamshell/shell.py)
- The checks showed the PS2 joystick forced a 24 mm-thick base. Swapped it for a low-profile Joy-Con-style stick.
- Decided to drop the clamshell for a desk dock with a detachable controller, closer to the final v1.

## 2026-11-08 — Companion app works end to end; parts ordered
- The Python companion app receives a task over WebSocket, runs Claude Code, and streams tool and done events back. Tested on Windows.
- Parts ordered from AliExpress, keeb.io and Amazon; soldering station and multimeter for the bench.
- Created this repo.

## 2026-11-07 — Spec
- First spec: a physical controller for AI coding agents, inspired by SlashVibe. → [spec (superseded)](docs/agent-controller-v0-spec.md)
