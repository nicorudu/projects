# AI Agent Controller v0 Prototype Spec

Written Nov 7, 2026. Personal learning build — not a commercial product.

## Goal

Build a handheld, Game Boy-style physical controller that lets you monitor and
direct AI coding agents (Claude Code, Codex, Cursor, etc.) without touching
the keyboard or switching windows on the Mac. Target: a working demo in about
3–4 weeks, built from off-the-shelf parts and a 3D printer.

**Core interaction**
- Glance at the display: see which agents are running, idle or waiting.
- Flick the joystick: cycle between agent sessions.
- Press a key: approve, reject, or send a canned command.
- Hold the mic button and speak: send a voice instruction to the active agent.
- The device stays in your hand or sits on the desk. The Mac does the work.

**Use cases**
- Running multiple Claude Code sessions at once and approving steps without
  switching focus away from a document or browser.
- Sending quick steering commands ("continue", "stop", "explain that") by
  voice while doing something else.
- Watching agent progress on a small dedicated screen so the main display
  stays uncluttered.

---

## v0 Architecture (deliberately chunky)

The v0 is a thick 3D-printed shell — not a polished product. It proves the
interaction and the firmware-to-companion-app pipeline. Form factor is refined
in v1.

### Form factor
- Handheld clamshell, roughly Game Boy Advance SP proportions.
- Top half: display.
- Bottom half: keys, joystick, mic button, speaker grille.
- Folds flat to about 25 mm thick for the prototype; thinner in v1.
- Hinge is a printed living-hinge or a simple barrel hinge for v0.

---

## Parts list (approx. $80–120)

| Part | Notes |
|---|---|
| ESP32-S3 dev board (e.g. XIAO ESP32-S3 or similar compact form) | Built-in Wi-Fi + BLE, I2S audio, USB-C, good flash. The S3 is the right chip for display + audio + wireless together. |
| 3.5–4.0 inch IPS SPI display, 320×480 or 480×320 | ST7796 or ILI9488 driver. SPI at 40 MHz is fast enough for LVGL at 30 fps. Cheap and widely available. |
| Kailh low-profile mechanical switches × 6 | Choc v1 or ultra-low-profile. 4 action keys + 1 mic/voice key + 1 back/cancel key. 1.8 mm travel feels snappy without bulk. |
| 2-axis analog thumbstick module | The kind used in Arduino joystick shields. Two 10 kΩ pots + center click. Reads on two ADC pins. |
| INMP441 MEMS microphone (I2S) | Very small, good sensitivity, runs on 3.3 V. Directly supported by the ESP32-S3's I2S peripheral. |
| MAX98357A I2S amplifier + small 8Ω speaker (1–2 W) | For audio feedback and read-back of agent status. |
| 3.7 V LiPo, 1000–1500 mAh | Enough for a full workday (target 6+ hours). Fits inside the bottom half of the shell. |
| LiPo charger board (TP4056 or matching the ESP32-S3 board's onboard charger) | USB-C charging while the device is docked on the desk. |
| Thin silicone wire, 28 AWG | Flexible runs between the two halves through the hinge. |
| Tactile push-buttons × 2 (optional) | Shoulder buttons for quick prev/next agent. |
| 3D printer filament: PETG for the shell, TPU for grips | PETG is stiff and prints clean. TPU side grips make it comfortable to hold. |
| M2 screws and heat-set inserts | Shell assembly. |

**Total estimated BOM:** $80–120 depending on display and switches sourced.

---

## Printed parts

1. **Top shell (display half):** holds the display, a bezel, and the hinge
   attachment. Print with the display opening face-down.
2. **Bottom shell (control half):** holds the ESP32-S3 board, battery,
   switches, joystick, mic and speaker. Main body of the device.
3. **Key caps:** 6 custom caps that fit the Choc switches. Print in a
   contrasting colour.
4. **Hinge barrel:** two interlocking pieces plus a printed pin, or just a
   real 20 mm barrel hinge from hardware. Test both.
5. **Desk stand:** a simple cradle that holds the device open at ~120° for
   desktop use. Prints in 20 minutes.

Print the shell in PETG at 0.2 mm layers, 3 walls, 20% infill. Sandpaper
finish at 400–800 grit for a matte look.

---

## Display and UI (LVGL)

Use **LVGL** (Light and Versatile Graphics Library) on the ESP32-S3.
It runs well on the S3 at 30 fps on a 480×320 SPI display with a small
frame buffer and DMA.

### Screens

**Home screen (always-on)**
```
┌─────────────────────────────┐
│  ● Claude Code  ACTIVE  ··· │  ← active agent, spinner
│  ○ Codex        IDLE        │
│  ○ Cursor       WAITING     │
│  ○ Agent 4      —           │
├─────────────────────────────┤
│  "Fix auth bug in login"    │  ← last instruction sent
│  Step 3 of 7 · 2 min ago   │
├─────────────────────────────┤
│  [✓ Approve]  [✗ Reject]   │  ← mapped to left/right action keys
│  [↑ Next step] [🎙 Speak]  │
└─────────────────────────────┘
```

**Agent detail screen (joystick click or select key)**
- Full last output from the active agent (scrollable with joystick up/down).
- Current step, file being edited, last tool call.
- Approve / reject / ask a question.

**Voice screen (mic button held)**
- Full screen: waveform animation while recording.
- Shows live transcription text from the companion app.
- Releases on button release; instruction is sent immediately.

**Status bar (always visible at top)**
- Battery percentage and charging indicator.
- Wi-Fi or BLE connection indicator.
- Clock.

---

## Firmware (Arduino framework on ESP32-S3)

### Key subsystems

**Display driver**
- LVGL with ST7796/ILI9488 SPI driver.
- Double-buffer DMA for smooth updates.
- Brightness controlled by PWM on the display backlight pin.

**Input handler**
- Reads joystick ADC every 20 ms; applies a small deadband (±5% of full
  range). Maps to scroll up/down and agent prev/next.
- Debounces each key with a 20 ms window.
- Mic button: starts I2S capture on press, stops on release.

**Audio**
- I2S microphone → ring buffer → send to companion app as raw PCM or
  compressed.
- I2S speaker: companion app streams TTS audio back for status read-back.
  Optional for v0; test the mic path first.

**Connectivity**
Two modes to test (same as the ring spec pattern):

1. **Wi-Fi (primary):** connects to the local network, talks to the
   companion app over a local WebSocket on port 8765. Lower latency
   than BLE for streaming audio. Easier to debug.
2. **BLE GATT (fallback / mobile use):** a custom service with
   characteristics for agent status, commands and audio chunks.
   Better for use away from a desk.

Start with Wi-Fi mode; BLE can be added after the core loop works.

**Protocol (device ↔ companion app)**

```
// Device → App
{ "type": "cmd",     "payload": "approve" }
{ "type": "cmd",     "payload": "reject"  }
{ "type": "cmd",     "payload": "next_step" }
{ "type": "audio",   "payload": "<base64 PCM chunk>" }
{ "type": "ping" }

// App → Device
{ "type": "state",   "agents": [ { "name": "Claude Code", "status": "active",
                                    "step": 3, "total": 7,
                                    "last_msg": "Editing auth.ts" } ] }
{ "type": "transcript", "text": "Fix the login bug" }
{ "type": "tts",        "payload": "<base64 audio>" }
{ "type": "pong" }
```

**Heartbeat / fail-safe**
- Device sends a ping every 500 ms.
- If the companion app stops responding for 2 s, the display shows a
  "disconnected" banner and locks out approve/reject until reconnected.
  Prevents accidental approvals while offline.

**Power management**
- Display dims after 30 s of no input (adjustable).
- ESP32-S3 light sleep when display is off; wakes on any key press or
  incoming WebSocket message.
- Target active draw: < 150 mA (display on, Wi-Fi connected).
  At 1200 mAh that is about 8 hours.

---

## Companion App (Mac, runs in the background)

A lightweight Python or Node.js process that:

1. **Bridges to AI agent sessions:** reads agent status from Claude Code,
   Codex, Cursor, etc. via their APIs, file watchers, or terminal
   session parsing (depending on what each tool exposes). Start with
   Claude Code, since it has the most accessible output.
2. **Runs a WebSocket server** on `localhost:8765` that the device
   connects to.
3. **Handles voice:** receives PCM audio from the device, sends it to
   Whisper (local via `whisper.cpp` or the OpenAI API), gets the
   transcript back, and passes it to the active agent session.
4. **Pushes state updates** to the device every 500 ms (or on any
   change).

### Claude Code integration (first target)
- Claude Code writes structured output to its log. The companion app
  tails that log and parses running/idle/waiting/error states and
  the current tool call.
- Approve / reject maps to sending the relevant key input to the
  Claude Code terminal session (via `pty` / `osascript` / Claude
  Code's own API if one is available).

### v0 scope
- Support one agent (Claude Code) at a minimum.
- Add Codex and Cursor once the Claude Code path is proven.
- Keep the companion app a plain terminal process for v0; a menu-bar
  app comes in v1.

---

## Build plan

**Week 1 — electronics breadboard**
- Wire up ESP32-S3 + display on a breadboard.
- Get LVGL running with the home screen (static data, no real agents).
- Add joystick and two keys; test navigation.
- Establish Wi-Fi WebSocket connection to a test server on the Mac.
- Pass: home screen updates live from the Mac when you push test JSON.

**Week 2 — voice + companion app**
- Add INMP441 mic; capture audio on button hold, stream to Mac.
- Build the companion app: Whisper transcription, Claude Code log
  parsing, WebSocket server.
- Pass: speak a phrase, see the transcript appear on the display.

**Week 3 — shell + assembly**
- Design and print the two-half shell.
- Mount all components, run wires through the hinge.
- Solder switches and joystick to the board.
- Pass: fully wireless, hand-holdable device working end to end.

**Week 4 — real agent loop**
- Run a real Claude Code session on the Mac Mini.
- Watch its status on the device; approve a step from the device.
- Send a voice instruction that changes what the agent does next.
- Pass: complete the success criteria below.

---

## Test plan

- Agent status updates on the device within 1 s of a change on the Mac.
- Approve / reject from the device reaches Claude Code reliably (10/10 presses).
- Voice instruction recognised correctly at least 8/10 times in a quiet room.
- Battery lasts at least 4 hours continuous use (target 6+).
- Switching between agents (once a second one is wired up) takes < 0.5 s.
- Display readable in a normally lit room without strain.
- Device stays connected over Wi-Fi for a 1-hour session with no drops.

---

## Success criteria for v0

- Approve a Claude Code step without touching the keyboard.
- Send a voice instruction that the agent acts on.
- Monitor 2+ agent sessions on the display simultaneously.
- Battery lasts a full work session (4+ hours).
- Fits comfortably in one hand for 10 minutes.

---

## Open questions

- Best Claude Code integration point: log file tail, `--output-format json`,
  terminal session PTY, or a future official API?
- Whisper local (`whisper.cpp` on the M4 Mac Mini) vs. OpenAI API for
  transcription latency — test both.
- Does the ESP32-S3 have enough RAM for LVGL + Wi-Fi + I2S audio at once?
  The S3 has 512 KB SRAM plus optional PSRAM; a board with 8 MB PSRAM is
  strongly preferred.
- Hinge: printed living hinge (simple, may fatigue) vs. a real barrel hinge
  (more durable, harder to print around)?
- Speaker: is audio read-back of agent status actually useful, or is the
  display enough for v0?

---

## Next step: v1 (after v0 passes)
- Custom PCB with ESP32-S3-WROOM, PSRAM, USB-C PD charging, pogo-pin
  charging contacts.
- Sandblasted anodised aluminium shell (outsourced CNC + anodising).
- Proper mechanical switches with custom aluminium key caps.
- Menu-bar companion app with per-agent icons and notifications.
- BLE mode polished for use away from the desk.
- Developer SDK so other tools can push status to the device.
