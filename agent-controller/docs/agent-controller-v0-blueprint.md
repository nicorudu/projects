# AI Agent Controller — Locked v0 Blueprint
Nov 7–8, 2026. Personal build. Updated with SlashVibe competitive intel and
technical corrections from initial build session.

---

## Competitive context: SlashVibe (slashvibe.ai)

Studied Nov 8, 2026 from their website (Kickstarter launches Nov 10, 2026,
ships March 2027).

| Spec | SlashVibe V1 | Our v0 |
|---|---|---|
| Display | 3.96" LCD | 4.0" ST7796 SPI |
| Connection to computer | USB-C data + power | Wi-Fi WebSocket |
| Controller connection | 2.4 GHz to display unit | Same device (clamshell) |
| Form factor | Two-piece: desk display + detachable handheld | Clamshell (Game Boy-style) |
| Battery | 500 mAh, 20 hours | 1000 mAh, target 6+ hours |
| Mic | Dual MEMS | Single INMP441 |
| Speaker | 2W | 1W |
| Shell | Sandblasted anodised aluminium | 3D-printed PETG (v0) |
| Price | $149 early bird / $249 retail + $8–14/mo software | Build cost ~$70–90 |
| Ships | March 2027 | We build first |
| Agents supported | 20+ (Claude Code, Codex, Cursor, Gemini CLI, etc.) | Claude Code first, expand later |

**Key insight:** Their architecture is USB-C to computer + 2.4 GHz between
the two halves. Our Wi-Fi WebSocket approach is different and potentially more
flexible (works across the room, works over a home network). We keep Wi-Fi
for v0; v1 can add USB-C if wired latency is preferable.

**Feature gap we can close:** SlashVibe has a developer SDK for custom
dashboards and agent integrations. We should plan an SDK or open protocol
in v1.

---

## 1. What we're building (locked form factor)

A clamshell desktop/handheld controller. Closed it looks like a small compact;
open it looks like a baby laptop sitting on the desk. The top half is the
screen. The bottom half has three wide flat buttons on the left and a large
rotary dial on the right.

```
  OPEN (side view)
  ┌─────────────────────┐
  │   4" DISPLAY        │  ← top half, hinged at back
  ├─────────────────────┤  ← hinge
  │  [BTN1][BTN2][BTN3] │  ← three wide flat buttons
  │               (◎)   │  ← large rotary encoder/dial
  └─────────────────────┘  ← bottom half

  CLOSED (face down on desk or in pocket)
  ┌─────────────────────┐
  │  logo / branding    │
  └─────────────────────┘
```

**Dimensions (target, to refine after printing)**
- Bottom shell: ~140 mm wide × 85 mm deep × 18 mm tall
- Top shell (display): ~140 mm wide × 90 mm tall × 8 mm thick
- Total closed: ~140 × 85 × 26 mm

---

## 2. Exact parts list (locked, verified compatible)

| # | Part | Why this one | Est. cost |
|---|---|---|---|
| 1 | **ESP32-S3 N16R8 dev board** (Freenove or similar DevKitC-1) | 16 MB flash, 8 MB PSRAM, 27+ free GPIOs, USB-C, Wi-Fi + BLE, LiPo charge circuit onboard. PSRAM mandatory — LVGL + Wi-Fi + I2S audio together need it. Order the PSRAM board, not the N8 variant. | ~$9 AliExpress |
| 2 | **4.0" IPS SPI display, 320×480, ST7796S driver** (Hosyond or LCDWIKI) | SPI uses only 5 pins; LVGL has a built-in ST7796 driver; 320×480 is plenty for our UI. Get the capacitive touch version with FT6336U. | ~$10 AliExpress |
| 3 | **EC11 rotary encoder with push button, 20mm shaft** | 20 detents/rev, integral push-click. Main navigation dial. | ~$2 AliExpress (5-pack) |
| 4 | **3× Kailh Choc v1 switches** (Red or Brown) | Low-profile, 1.8 mm travel, confirmed used in SlashVibe. | ~$3 keeb.io |
| 5 | **Blank Choc keycaps × 5** | MBK profile blank white. | ~$5 keeb.io |
| 6 | **INMP441 MEMS microphone module** (I2S) | 3.3V, I2S output. Direct I2S to ESP32-S3. | ~$1 AliExpress |
| 7 | **MAX98357A I2S amplifier breakout + 1W 8Ω speaker** | I2S in, speaker out. | ~$1 AliExpress |
| 8 | **LiPo 1000 mAh, 3.7V, with protection circuit, JST-PH 2.0mm** | ⚠️ Order from Amazon, not AliExpress — LiPo shipping from China is unreliable. | ~$9 Amazon |
| 9 | **WS2812B mini LED × 1** | Status indicator visible through shell. | ~$1 AliExpress |
| 10 | **28 AWG silicone wire** | Runs through hinge. Silicone flexes without cracking. | ~$3 AliExpress |
| 11 | **M2 × 6mm button-head screws + heat-set inserts** | Shell assembly. | ~$4 AliExpress |
| 12 | **40mm 8Ω 1W mini speaker** | Audio feedback. | ~$2 AliExpress |
| 13 | **Small barrel hinge, 20mm** | Sturdier than a printed hinge. | ~$2 AliExpress |

**Total BOM: ~$52**

---

## 3. Pin map (ESP32-S3, locked)

```
PERIPHERAL          SIGNAL      GPIO    NOTES
─────────────────────────────────────────────────────────
DISPLAY (SPI2)
  ST7796S           MOSI        GPIO11
                    CLK         GPIO12
                    CS          GPIO10
                    DC          GPIO9
                    RST         GPIO3
                    BL (PWM)    GPIO8   Backlight, LEDC ch0

TOUCH (I2C)
  FT6336U           SDA         GPIO1
                    SCL         GPIO2
                    INT         GPIO4   Active-low interrupt

ROTARY ENCODER
  EC11              CLK (A)     GPIO5
                    DT  (B)     GPIO6
                    SW  (push)  GPIO7

BUTTONS
  BTN1 (approve)                GPIO15  Pull-up, active-low
  BTN2 (back/cancel)            GPIO16  Pull-up, active-low
  BTN3 (mic/voice)              GPIO17  Pull-up, active-low

I2S MICROPHONE (INMP441) — uses I2S0
                    BCK         GPIO35
                    WS (LRCK)   GPIO36
                    SD (data)   GPIO37

I2S SPEAKER (MAX98357A) — uses I2S1
  ⚠️ CORRECTION: use a SEPARATE I2S peripheral (I2S1), not shared.
  Share the PHYSICAL BCK and WS wires (ESP32-S3 drives both
  as master), but configure as two distinct peripheral instances.
                    BCK         GPIO35  Shared physical wire with mic BCK
                    LRC (WS)    GPIO36  Shared physical wire with mic WS
                    DIN         GPIO38  Separate data pin
                    SD_MODE     3V3     Tie high = always on

STATUS LED
  WS2812B           DIN         GPIO21

UART (debug)
                    TX          GPIO43
                    RX          GPIO44
─────────────────────────────────────────────────────────
FREE GPIOs: GPIO13, GPIO14, GPIO18, GPIO39–42, GPIO47, GPIO48
```

---

## 4. Shell design (3D print plan)

Four printed parts: bottom shell (controls + board + battery), top shell
(display lid), 3× keycaps, dial cap. Print in PETG, 0.2 mm layers, 4 walls,
20% gyroid. Hinge wire bundle: 6 wires (3.3V, GND, MOSI, CLK, CS, DC).

**⚠️ Do NOT finalize shell dimensions until parts arrive.** Measure every
component with calipers. Clone board dimensions vary from datasheets.

---

## 5. Firmware architecture (ESP32-S3, Arduino framework)

### ⚠️ Known issue: ST7796 color byte-swap on ESP32-S3

The ST7796 on ESP32-S3 with LVGL has a well-documented color problem
(garbled or wrong colors) caused by `LV_COLOR_16_SWAP` being set incorrectly.

**Fix:** Set `LV_COLOR_16_SWAP 0` in `lv_conf.h`. Let SPI DMA handle byte
order. Start SPI at **20 MHz** (not 40 MHz) for initial bring-up. Increase
to 40 MHz only after display is stable.

Reference: Confirmed working setup on ESP32-S3 from esp32.com forums.

### ⚠️ I2S: use separate peripherals for mic and speaker

Do NOT use half-duplex mode switching between mic and speaker on the same
I2S peripheral. Instead:
- I2S0: microphone (RX mode), INMP441
- I2S1: speaker (TX mode), MAX98357A
- Both can share the PHYSICAL BCK and WS wires because the ESP32-S3 drives
  them as master for both. Use separate `i2s_chan_handle_t` instances.

This avoids mode-switching complexity and is the community-validated approach
for INMP441 + MAX98357A on ESP32-S3.

### Module breakdown

```
firmware/
  agent_controller/
    agent_controller.ino   Main sketch
    config.h               All pins, timing constants, Wi-Fi creds (gitignored)
    config.h.example       Template with placeholder values
    display.h / .cpp       LVGL init, screen management, draw calls
    input.h   / .cpp       Encoder ISR, button debounce, event queue
    audio.h   / .cpp       I2S0 mic capture, I2S1 speaker playback
    network.h / .cpp       Wi-Fi connect, WebSocket client, reconnect loop
    protocol.h / .cpp      JSON encode/decode
    led.h     / .cpp       WS2812B status animation
    power.h   / .cpp       Backlight dimming, light sleep
```

### Task layout (FreeRTOS)

```
Core 0: network_task (Wi-Fi + WebSocket rx/tx), audio_task (I2S DMA)
Core 1: ui_task (LVGL tick, 33ms), input_task (encoder + buttons), main_task (state machine)
```

---

## 6. Companion app (Python, cross-platform)

### Platform support
**Primary: Mac** (Claude Code sessions on Mac Mini).
**Secondary: Windows** (HP OmniBook — tested and working).

The companion app is pure Python and runs identically on both platforms.
Install Python 3.11+ and run `pip install websockets` on each machine.
The `claude` subprocess call uses the PATH-resolved binary, which works
on Mac and Windows without code changes.

**To install on Mac:** copy `main.py` to the Mac Mini and run it there
so the WebSocket server is on the same machine as Claude Code sessions.

### ⚠️ Correction from v0 build: `--dangerously-skip-permissions` mode

The original blueprint described a PTY wrapper with y/n approval flow.
The v0 companion app was built and tested using `--dangerously-skip-permissions`
instead, which auto-approves all tool use. This was chosen for v0 simplicity.

**What this means:** in v0, pressing BTN1 (approve) on the device does NOT
gate individual tool calls. Claude Code runs fully autonomously. The device
shows live tool calls and the final result. Approval gating is deferred to v1.

**v1 plan:** use `pywinpty` (Windows) or `pty` (Mac/Linux) for a proper PTY
wrapper that pauses on approval prompts and waits for button input.

### Tested protocol (wire format)

```json
// Device → App
{ "t": "ping" }
{ "t": "task", "task": "create a file called hello.txt with the word hello" }

// App → Device
{ "t": "pong" }
{ "t": "status", "msg": "running" }
{ "t": "tool",   "tool": "Write", "input": "..." }
{ "t": "text",   "msg": "..." }
{ "t": "done",   "result": "...", "error": false }
```

### Running as a background service (Windows)

```powershell
# Kill any existing instance
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
# Start as background job
Start-Job -ScriptBlock { python C:\Users\natio\agentcontroller\agent-controller\companion-app\main.py }
```

---

## 7. Build sequence (4 weeks, starting when parts arrive)

### Week 1 — Display + encoder on breadboard
Wire ESP32-S3 + ST7796 per pin map. Flash LVGL. Start SPI at 20 MHz.
Confirm `LV_COLOR_16_SWAP 0` fixes colors. Add encoder and buttons.
Build home screen with static data.
Gate: screen renders at 25+ fps, encoder scrolls list.

### Week 2 — Network + companion app integration
Add Wi-Fi + WebSocket client. Install companion app on Mac Mini.
Confirm full round-trip: task from device → Claude Code runs on Mac →
tool and done events back to device.
Gate: live Claude Code status on device display.

### Week 3 — Voice + I2S
Wire INMP441 on I2S0, MAX98357A on I2S1. Stream mic to companion app.
Companion app transcribes with Whisper (local on Mac Mini M4 is fast enough
for the `small` model). Transcript appears on device.
Gate: speak a sentence, see it transcribed on screen.

### Week 4 — Shell + final assembly
Print after measuring all components. Assemble. Run test plan.
Gate: all success criteria met.

---

## 8. Test plan

| Test | Pass condition |
|---|---|
| Display | Home screen at ≥25 fps with Wi-Fi active |
| Encoder | Scroll through 4 agents, no missed steps |
| Buttons | BTN1/2/3 register, 20/20 presses |
| Task execution | Claude Code completes a task, done message arrives on device |
| Tool streaming | Tool events appear on device in real time |
| Voice | 10-word sentence transcribed correctly ≥8/10 |
| Reconnect | Drop Wi-Fi, restore → device reconnects within 10 s |
| Battery | 4+ hours continuous use |
| Fit | Comfortable to hold for 10 minutes |
| Hinge | Opens and closes 50× without wire damage |

---

## 9. Open questions

1. **Mac companion app deployment** — auto-launch on login (launchd plist) vs
   manual start. Decide before Mac install.
2. **Whisper model size** — `small` (~500MB) vs `medium` (~1.5GB) on M4 Mac
   Mini. Test transcription latency on first recording.
3. **TTS in v0** — is speaker read-back actually useful? Build it last.
4. **Wi-Fi credentials** — stored in `config.h` (gitignored). For v1, add a
   BLE provisioning flow.
5. **Multi-agent launch** — for v0, all Claude Code sessions started manually.
   Auto-launch from device is v1.
6. **Companion app on both Mac and Windows** — install and test on Mac Mini
   first (primary), then Windows laptop (secondary).

---

## 10. What v1 adds (after v0 passes)
- CNC aluminium shell, anodized matte silver (matching SlashVibe aesthetics).
- Custom PCB with ESP32-S3-WROOM, USB-C PD, pogo-pin charging.
- Proper PTY approval flow (y/n from device buttons).
- 2.4 GHz wireless option for the controller (matching SlashVibe's detachable
  controller approach).
- Companion app as a macOS menu-bar app with auto-launch.
- Developer SDK: open WebSocket protocol spec so any tool can push status.
- Expand agent support: Codex, Cursor, Gemini CLI, OpenCode (match SlashVibe's
  20+ agent list).
- Windows companion app packaged as an .exe.
