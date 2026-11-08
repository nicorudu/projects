# AI Agent Controller — Locked v0 Blueprint
Nov 7, 2026. Personal build. Updated from SlashVibe teardown photos.

---

## 1. What we're building (locked form factor)

A clamshell desktop/handheld controller. Closed it looks like a small compact;
open it looks like a baby laptop sitting on the desk. The top half is the
screen. The bottom half has three wide flat buttons on the left and a large
rotary dial on the right. That's the entire physical interface — no joystick,
no extra keys. Simple and direct.

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
  │  SlashVibe logo     │
  └─────────────────────┘
```

**Dimensions (target, to refine after printing)**
- Bottom shell: ~140 mm wide × 85 mm deep × 18 mm tall
- Top shell (display): ~140 mm wide × 90 mm tall × 8 mm thick
- Total closed: ~140 × 85 × 26 mm — fits in a large shirt pocket

---

## 2. Exact parts list (locked, verified compatible)

| # | Part | Why this one | Est. cost |
|---|---|---|---|
| 1 | **ESP32-S3-WROOM-1-N16R8 dev board** (Freenove or Olimex ESP32-S3-DevKit-Lipo) | 16 MB flash, 8 MB PSRAM, 27+ free GPIOs, USB-C, Wi-Fi + BLE, LiPo charge circuit onboard. PSRAM is mandatory — LVGL + Wi-Fi + I2S audio together need it. | ~$15 |
| 2 | **4.0" IPS SPI display, 320×480, ST7796S driver** (LCDWIKI MSP4031 or equivalent) | SPI uses only 5 pins; LVGL has a built-in ST7796 driver; 320×480 is plenty for our UI. MIPI (what SlashVibe uses) is NOT supported by ESP32-S3 natively — we use SPI for v0. | ~$18 |
| 3 | **FT6336U capacitive touch breakout** (I2C) | Optional for v0 but good to wire in now. Lets us tap the screen as a shortcut. Already integrated on most ST7796 panels above — confirm before buying separately. | $0 if bundled |
| 4 | **EC11 rotary encoder with push button** | 20 detents/rev, integral push-click. This is the main navigation dial. Standard part, works on any GPIO. | ~$2 |
| 5 | **3× Cherry MX-style low-profile switches + large blank keycaps** (Kailh Choc v1) | Wide, flat, satisfying click, 1.8 mm travel. The big keycaps make them look like SlashVibe's wide buttons. Order white keycaps; paint or laser-engrave icons. | ~$8 |
| 6 | **INMP441 MEMS microphone module** (I2S) | 3.3 V, I2S output, tiny. Direct I2S to ESP32-S3. No analog noise path. | ~$3 |
| 7 | **MAX98357A I2S amplifier breakout + 1 W 8Ω speaker** | I2S in, speaker out. For audio feedback and optional TTS read-back. Runs off 3.3 V. | ~$5 |
| 8 | **LiPo 1000 mAh, 3.7 V, with protection circuit** | Fits inside the bottom shell. Target >6 h run time at ~120 mA average draw. | ~$8 |
| 9 | **WS2812B mini LED × 1** (optional status indicator) | One RGB pixel visible through the shell = battery, connection, agent status at a glance without looking at the screen. | ~$1 |
| 10 | **PETG filament** (shell) + **TPU 95A** (grip pads) | PETG for the rigid shell. TPU strips glued to the sides and back for grip. | ~$5 of filament |
| 11 | **M2 × 6 mm button-head screws + heat-set inserts** | Shell assembly. | ~$3 |
| 12 | **28 AWG silicone wire** | Runs through the hinge between the two halves (display power + SPI). Silicone flexes without cracking. | ~$3 |
| 13 | **Small barrel hinge, 20 mm** | Sturdier than a printed hinge for something opened 10× a day. Source from hardware store or AliExpress. | ~$2 |

**Total BOM: ~$70–90**

---

## 3. Pin map (ESP32-S3, locked)

The ESP32-S3-WROOM-1 has GPIOs 0–21 and 35–48 available (GPIO22–32 are
internal flash/PSRAM). We avoid 0 (bootstrap) and 45–46 (bootstrap/LED on
some boards — check your specific board's datasheet).

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

I2S MICROPHONE (INMP441)
                    BCK         GPIO35
                    WS (LRCK)   GPIO36
                    SD (data)   GPIO37

I2S SPEAKER (MAX98357A)
                    BCK         GPIO35  SHARED with mic BCK
                    LRC (WS)    GPIO36  SHARED with mic WS
                    DIN         GPIO38
                    SD_MODE     3V3     Tie high = always on

STATUS LED
  WS2812B           DIN         GPIO21

UART (debug, USB-UART chip on dev board)
                    TX          GPIO43  (default on most S3 boards)
                    RX          GPIO44

USB (native USB on ESP32-S3)
                    D+          GPIO20  (internal, don't use)
                    D-          GPIO19  (internal, don't use)
─────────────────────────────────────────────────────────
FREE GPIOs remaining: GPIO13, GPIO14, GPIO18, GPIO39–42, GPIO47, GPIO48
Use for future expansion (second mic, haptic motor, etc.)
```

**I2S mic and speaker share BCK and WS** — this is standard half-duplex
practice. The ESP32-S3 runs them on the same I2S peripheral in simplex mode:
mic active while recording, amplifier active during playback. They cannot
run simultaneously, which is fine for push-to-talk.

**SPI2 at 40 MHz** is the right bus for the ST7796. LVGL with DMA double-
buffering at this speed gives ~30 fps on a 320×480 panel, which is smooth
enough for a status UI.

---

## 4. Shell design (3D print plan)

### Four printed parts

**Part A — Bottom shell**
Holds: ESP32-S3 board, LiPo, speaker, three Choc switches, EC11 encoder,
mic module, status LED.
- Encoder mounts in the center-right of the face with a 7 mm hole.
- Three switch slots 18 mm × 14 mm each, spaced 4 mm apart, left side.
- Speaker grille: 20× 1.5 mm slots on the right of the base (facing down
  when open on a desk, or forward when held).
- Battery bay on the inside floor, recessed 6 mm.
- Dev board mounts on standoffs on the inside rear wall.
- Hinge barrel socket at the rear top edge.

**Part B — Top shell (display lid)**
Holds: 4" display, bezel frame.
- Display recess exactly sized for the ST7796 panel (confirm dimensions
  from the datasheet: ~96 mm × 64 mm active area).
- 1.5 mm bezel on all sides.
- Hinge barrel socket at the rear bottom edge, aligned with Part A.
- Wire channel along the hinge axis for the 6-wire ribbon (SPI + power)
  between halves.

**Part C — 3× Keycaps**
Wide, flat-top caps that snap onto Kailh Choc v1 stems.
- Face: ~22 mm × 14 mm, 2 mm thick, 0.5 mm travel clearance.
- Icon: embossed symbols (✓, ↩, 🎙) or laser-engraved after printing.

**Part D — Dial cap**
Knob that presses onto the EC11 D-shaft.
- 32 mm diameter, 8 mm tall, knurled sides.
- Flush-top with a small center dot for orientation.

### Print settings
- Material: PETG (shell), TPU 95A (optional grip strip glued to sides).
- Layer height: 0.2 mm.
- Walls: 4 perimeters (strength for the hinge area).
- Infill: 20% gyroid.
- Supports: needed inside the display recess and hinge sockets only.

### Hinge wire routing
Run 6 wires through the hinge barrel (or alongside it in a small sleeve):
3.3 V, GND, MOSI, CLK, CS, DC. RST and BL can be pulled high/low with
resistors on the display side so they don't need dedicated wires through the
hinge. This keeps the hinge bundle to 6 wires.

---

## 5. Firmware architecture (ESP32-S3, Arduino framework)

### Module breakdown

```
firmware/
  agent_controller/
    agent_controller.ino   Main sketch — setup(), loop(), task spawning
    config.h               All pin numbers, timing constants, Wi-Fi creds
                           (gitignored — copy from config.h.example)
    display.h / .cpp       LVGL init, screen management, draw calls
    input.h   / .cpp       Encoder ISR, button debounce, event queue
    audio.h   / .cpp       I2S mic capture, I2S speaker playback
    network.h / .cpp       Wi-Fi connect, WebSocket client, reconnect loop
    protocol.h / .cpp      JSON encode/decode for the wire format
    led.h     / .cpp       WS2812B status animation
    power.h   / .cpp       Backlight dimming, light sleep
```

### Task layout (FreeRTOS, two cores)

```
Core 0 (Protocol CPU):
  Task: network_task     — Wi-Fi keep-alive, WebSocket rx/tx, ping/pong
  Task: audio_task       — I2S DMA read (mic) or write (speaker)

Core 1 (Application CPU):
  Task: ui_task          — LVGL tick, screen redraws, 33 ms period (30 fps)
  Task: input_task       — Polls encoder + buttons, pushes events to queue
  Task: main_task        — State machine, consumes events + network msgs
```

Queues:
- `input_queue` (depth 16): input_task → main_task
- `net_rx_queue` (depth 8): network_task → main_task
- `net_tx_queue` (depth 8): main_task → network_task
- `audio_queue` (depth 4): audio_task ↔ main_task (PCM chunk pointers)

### State machine (main_task)

```
States:
  DISCONNECTED   → no WebSocket connection. Screen shows "Connecting…"
  IDLE           → connected, no agents active. Screen shows agent list (all idle).
  ACTIVE         → ≥1 agent running or waiting for approval.
  RECORDING      → mic button held. Audio streaming to companion app.
  PLAYING        → companion app streaming TTS back.

Transitions:
  DISCONNECTED → IDLE        on WebSocket connected + first state msg received
  IDLE / ACTIVE → RECORDING  on BTN3 pressed
  RECORDING → IDLE/ACTIVE    on BTN3 released (send audio_end msg)
  IDLE/ACTIVE → ACTIVE       on state msg with ≥1 agent in RUNNING/WAITING
  ACTIVE → IDLE              on state msg with all agents IDLE/DONE
  any → DISCONNECTED         on WebSocket disconnect or ping timeout (2 s)
```

### Display screens (LVGL)

**Screen 0: Connecting**
Full-screen centered text: "Connecting to companion app…" + spinner.
Shown in DISCONNECTED state.

**Screen 1: Agent List (home)**
```
╔═══════════════════════════╗
║ ● CLAUDE CODE   WORKING ● ║  ← green dot, spinner
║ ○ CODEX         IDLE      ║
║ ○ CURSOR        WAITING ⚠ ║  ← yellow dot
║ ○ —             —         ║
╠═══════════════════════════╣
║ Fix auth bug in login.ts  ║  ← active agent last task (truncated)
║ Step 2 of 5 · 00:34       ║  ← step counter, elapsed time
╠═══════════════════════════╣
║  [✓ Approve]  [✗ Reject]  ║  ← shown only when agent WAITING
╚═══════════════════════════╝
  Battery 87%  ● WiFi
```
- Encoder rotation: scroll agent list up/down.
- Encoder push: enter Screen 2 (agent detail).
- BTN1: Approve (active only when agent WAITING).
- BTN2: Reject / Back.
- BTN3: Hold to record voice.

**Screen 2: Agent Detail**
Full last output from the selected agent, scrollable with encoder.
BTN2 goes back to Screen 1.

**Screen 3: Recording**
Full screen: waveform animation (animated sine) + live transcript text
as it arrives from the companion app.
Releases automatically on BTN3 release.

**Screen 4: Settings** (encoder long-press from Screen 1)
- Wi-Fi SSID/IP display (read-only)
- Backlight brightness (encoder adjusts)
- Companion app port
- Firmware version

### Input handler

```cpp
// encoder.cpp — ISR-driven quadrature decode
void IRAM_ATTR encoderISR() {
    static int8_t table[16] = {0,-1,1,0,1,0,0,-1,-1,0,0,1,0,1,-1,0};
    static uint8_t prev = 0;
    uint8_t curr = (digitalRead(ENC_A) << 1) | digitalRead(ENC_B);
    int8_t dir = table[(prev << 2) | curr];
    if (dir != 0) xQueueSendFromISR(input_queue, &dir, NULL);
    prev = curr;
}

// button.cpp — debounce in input_task
// Poll each button pin every 10 ms.
// Rising edge after 20 ms stable = press event.
// Held >500 ms = long-press event.
// Encoder SW: same logic, also generates long-press for settings.
```

### Protocol (wire format)

All messages are newline-delimited JSON over WebSocket.

```json
// Device → App
{ "t": "ping" }
{ "t": "cmd",   "cmd": "approve" }
{ "t": "cmd",   "cmd": "reject"  }
{ "t": "cmd",   "cmd": "next"    }
{ "t": "audio", "seq": 42, "pcm": "<base64 raw 16-bit 16kHz mono>" }
{ "t": "audio_end" }

// App → Device
{ "t": "pong" }
{ "t": "state", "agents": [
    { "id": "cc1", "name": "Claude Code",
      "status": "waiting",   // idle | running | waiting | done | error
      "task":  "Fix auth bug in login.ts",
      "step":  2, "steps": 5,
      "elapsed": 34 }
  ]
}
{ "t": "transcript", "text": "Fix the login bug" }
{ "t": "tts", "seq": 1, "pcm": "<base64>" }
{ "t": "tts_end" }
```

Ping every 500 ms. If 4 consecutive pings go unanswered (2 s), device
drops to DISCONNECTED and reconnects.

---

## 6. Companion App architecture (Mac, Python 3.11+)

```
companion/
  main.py              Entry point. Starts all services.
  config.py            Port, Whisper model, paths (gitignored for creds)
  ws_server.py         WebSocket server on localhost:8765
  agent_manager.py     Tracks all agent sessions, pushes state updates
  claude_code.py       Claude Code integration (PTY wrapper)
  whisper_stt.py       Whisper transcription (local or API)
  tts.py               Text-to-speech (macOS `say` for v0, Kokoro later)
  protocol.py          Message encode/decode matching firmware protocol.h
```

### ws_server.py
Runs `websockets.serve()` on `localhost:8765`. One connected device at a
time. On connect: immediately sends current agent state. On message:
dispatches to `agent_manager` (cmd) or `whisper_stt` (audio chunks).

### claude_code.py — PTY wrapper (key integration)
This is the most important and trickiest module.

```python
import pty, os, select, re

class ClaudeCodeSession:
    """
    Wraps one `claude` process in a PTY so we can:
      1. Read its output stream and parse status.
      2. Inject keystrokes (y/n/Enter) for approvals.
    """
    def __init__(self, working_dir, task):
        self.status = "running"   # running | waiting | idle | done | error
        self.task   = task
        self.step   = 0
        self.steps  = 0
        self._last_output = ""
        master_fd, slave_fd = pty.openpty()
        self._master = master_fd
        self._pid = os.fork()
        if self._pid == 0:          # child
            os.chdir(working_dir)
            os.execvp("claude", ["claude", "--output-format", "stream-json",
                                  "--print", task])
        # parent: read master_fd in a thread

    def _read_loop(self):
        while True:
            r, _, _ = select.select([self._master], [], [], 0.1)
            if r:
                data = os.read(self._master, 4096).decode(errors="replace")
                self._parse(data)

    def _parse(self, data):
        # Claude Code stream-json emits one JSON object per line
        for line in data.splitlines():
            try:
                msg = json.loads(line)
            except:
                continue
            if msg.get("type") == "tool_use":
                self.status = "running"
                self.step  += 1
            elif msg.get("type") == "tool_result_pending_approval":
                self.status = "waiting"      # → device shows Approve/Reject
            elif msg.get("type") == "result":
                self.status = "done"
        self._last_output = data

    def approve(self):
        os.write(self._master, b"y\n")
        self.status = "running"

    def reject(self):
        os.write(self._master, b"n\n")
        self.status = "running"
```

> **Note on Claude Code's approval API:** Claude Code's exact stream-json
> schema needs to be verified against the real binary once you have it
> running. The type names above (`tool_result_pending_approval`, etc.) are
> best guesses — read the actual output of
> `claude --output-format stream-json --print "say hello"` and adjust.

### agent_manager.py
Holds a dict of `ClaudeCodeSession` objects keyed by session ID.
Every 500 ms, serialises all sessions into the `state` message and
broadcasts to the connected device via `ws_server`.

```python
def build_state_msg(sessions):
    return {
        "t": "state",
        "agents": [
            { "id": sid, "name": s.name, "status": s.status,
              "task": s.task, "step": s.step, "steps": s.steps,
              "elapsed": int(time.time() - s.start_time) }
            for sid, s in sessions.items()
        ]
    }
```

### whisper_stt.py
Receives base64 PCM chunks from the device, accumulates into a buffer,
then on `audio_end` message:
1. Writes raw 16-bit 16 kHz mono PCM to a temp `.wav` file.
2. Runs `whisper_timestamped` or `faster-whisper` locally (M4 Mac Mini
   handles the `small` or `medium` model in real time).
3. Returns transcript string to `agent_manager`, which routes it as a
   new instruction to the active session.

For v0, the OpenAI Whisper API is acceptable as a fallback if local is slow.

### tts.py (optional for v0)
Uses macOS built-in `say -v Samantha -r 200` piped to raw audio, then
encodes and streams back to the device as `tts` messages.
Test whether the speaker is actually useful before spending time here.

---

## 7. Build sequence (4 weeks)

### Week 1 — Display + encoder on breadboard
1. Wire ESP32-S3 dev board + ST7796 display on a breadboard per pin map.
2. Flash LVGL `hello_world` demo — confirm display works at 30 fps.
3. Add EC11 encoder; confirm scroll events appear in serial log.
4. Add 3 buttons; confirm debounced events.
5. Build Screen 1 (agent list) with static hardcoded data.
6. **Gate:** screen renders, encoder scrolls the list, buttons register.

### Week 2 — Network + companion app skeleton
1. Add Wi-Fi connect + WebSocket client to firmware.
2. Write `ws_server.py` + `protocol.py` on the Mac.
3. Send a fake `state` message from the Mac; confirm device screen updates live.
4. Send `approve` from the device; confirm Mac logs it.
5. **Gate:** full round-trip message loop working over Wi-Fi.

### Week 3 — Voice + Claude Code integration
1. Wire INMP441 mic; stream PCM to Mac on BTN3 hold.
2. Mac transcribes with Whisper; transcript appears on device Screen 3.
3. Write `claude_code.py`; run a real Claude Code session under the PTY.
4. Parse status and push to device.
5. Press BTN1 (Approve) on device; confirm Claude Code advances.
6. **Gate:** complete agent control loop working, end to end.

### Week 4 — Shell + final assembly
1. Print bottom shell; fit all components.
2. Print display lid; route hinge wires.
3. Print keycaps and dial; fit switches and encoder.
4. Assemble with M2 screws; test hinge.
5. Run the full test plan below.
6. **Gate:** all success criteria met.

---

## 8. Test plan

| Test | Pass condition |
|---|---|
| Display | Home screen renders at ≥25 fps with Wi-Fi active |
| Encoder | Scroll up/down through 4 agents, no missed steps |
| Buttons | BTN1/2/3 register on every press, 20/20 |
| Approve | BTN1 press → Claude Code advances within 1 s |
| Reject | BTN2 press → Claude Code cancels tool within 1 s |
| Voice | Speak a 10-word sentence → transcript correct ≥8/10 |
| State update | Agent status changes on Mac → device screen updates within 1 s |
| Reconnect | Pull Wi-Fi, restore → device reconnects within 10 s |
| Battery | 4+ hours continuous use at screen-on |
| Fit | Comfortable to hold for 10 minutes |
| Hinge | Opens and closes 50× without wire damage |

---

## 9. Open questions (decisions deferred to build)

1. **Claude Code approval API** — verify exact stream-json event names by
   running `claude --output-format stream-json` and reading real output
   before writing the PTY parser.
2. **Whisper model size** — `small` (~500 MB) vs `medium` (~1.5 GB) on
   the M4 Mac Mini. Test latency on first real recording.
3. **TTS in v0** — is speaker read-back actually useful? Build it last,
   after everything else works.
4. **Wi-Fi credentials** — stored in `config.h` (gitignored). For v1,
   add a BLE provisioning flow so credentials aren't hardcoded.
5. **Multi-agent launch** — for v0, all Claude Code sessions are started
   manually from the Mac terminal. The companion app discovers running
   sessions. Auto-launch from the device is a v1 feature.

---

## 10. What v1 adds (after v0 passes)
- CNC aluminium shell, anodized matte silver.
- Custom PCB (ESP32-S3-WROOM module, USB-C PD, pogo-pin charging contacts).
- MIPI DSI display (higher resolution, thinner lid).
- BLE mode for wireless use away from the desk.
- Companion app as a macOS menu-bar app with auto-launch on login.
- Developer SDK: a simple WebSocket protocol spec so any tool can push
  status to the device.
- Windows companion app.
