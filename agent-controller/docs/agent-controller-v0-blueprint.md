# AI Agent Controller — v0 Blueprint (rev 2)

Personal build. Rev 2 written Nov 11, 2026. It replaces the clamshell design from Nov 7–8 (rev 1) with a desk dock plus a detachable controller, adds a USB data path alongside Wi-Fi, the voice pipeline, and the platform plug-in plan.

Reference product notes: `claude/slashvibe-reference.md` in the Vibecodes project.

### What changed from rev 1
| Rev 1 (clamshell) | Rev 2 (dock + controller) |
|---|---|
| One clamshell body, everything wired to one ESP32-S3 | **Dock** (display, speaker, ESP32-S3 DevKitC) + **controller** (keys, stick, mics, battery, XIAO ESP32S3) |
| EC11 rotary encoder → PS2 joystick | Joy-Con-style mini analog stick (Adafruit #5628) |
| Mic in the base | 2 × INMP441 on the controller's joystick end |
| Wi-Fi only | Wi-Fi **and** USB data. Both get built, then compared. |
| I2S on GPIO35–38 | **Moved.** GPIO35–37 are taken by the octal PSRAM on N16R8 boards. See the pin map. |
| Display RST on GPIO3 | Moved to GPIO14 (GPIO3 is a strapping pin) |

---

## 1. What we're building

A desk workspace for AI agents, closely following SlashVibe's layout:

- **Dock:** a 4" screen on a fold-flat hinge at the back of a low base. A speaker grille sits in the base. It connects to the computer with one USB-C cable, which carries power and data.
- **Controller:** a straight bar with three keys (**Cancel / Voice / Send**), a flat-capped thumbstick at one end, two mics on that end face, and a status LED beside the stick.
  - Docked, it lies along the front edge of the base and charges through magnetic pogo pins.
  - Lifted off, it works as a wireless handheld.
  - On the desk, you turn the whole bar so the stick sits under your thumb. The stick does **not** swivel.

Primary computer is the M4 Mac Mini; the Windows laptop is secondary. Everything on the computer side is Python, so it runs on both.

---

## 2. System architecture

```
                         ┌──────────── Mac Mini (companion app, Python) ────────────┐
                         │  transports ─ protocol ─ voice pipeline ─ platform plug-ins │
                         └───────▲──────────────────────────────▲──────────────────┘
                     Path B: USB │ (CDC serial)          Path A: │ Wi-Fi (WebSocket :8765)
                                 │                               │
   ┌──────────── DOCK ───────────┴───┐                           │
   │ ESP32-S3 N16R8 DevKitC          │◄───── Wi-Fi (Path A) ─────┤
   │ 4" ST7796 + touch, amp, speaker │                           │
   │ LED, pogo female (5 V out)      │                           │
   └──────────────▲──────────────────┘                           │
       Path B:    │ ESP-NOW (2.4 GHz, ESP32↔ESP32)                │
   ┌──────────────┴──────────────────┐                           │
   │ CONTROLLER  XIAO ESP32S3        │───── Wi-Fi (Path A) ──────┘
   │ 3 Choc keys, stick, 2 mics, LED │
   │ 1000 mAh LiPo, TP4056, switch   │
   └─────────────────────────────────┘
```

The device side is a thin client. All the work happens on the computer: agent sessions, speech-to-text and AI cleanup. The dock draws what the computer tells it to and reports input. This is the same split SlashVibe uses.

### Two data paths, built side by side
| | Path A — Wi-Fi | Path B — USB (SlashVibe-style) |
|---|---|---|
| Dock ↔ Mac | WebSocket over Wi-Fi | USB CDC serial on the DevKitC's **native USB** port |
| Controller ↔ Mac | WebSocket over Wi-Fi, direct | ESP-NOW to the dock, then relayed over USB |
| Pros | Simple; works across the room | Lower and steadier latency; no Wi-Fi setup; controller radio idles more (better battery) |
| Cons | Wi-Fi jitter; controller radio draws more | Dock firmware has to relay; ESP-NOW bandwidth needs the audio kept compact |

Both paths carry the **same JSON messages** (section 5). The companion app has two interchangeable transports, and a setting picks which one is used. The dock and controller each support both, so we can flip between them and measure (section 9).

---

## 3. Parts

### Dock
| Part | Status |
|---|---|
| ESP32-S3 N16R8 DevKitC-1 (dual USB-C, pins soldered) | Ordered — AliExpress |
| 4.0" ST7796S 320×480 SPI LCD, FT6336U capacitive touch (LCDWIKI MSP4031) | Ordered — AliExpress |
| MAX98357A I2S amplifier | Ordered — AliExpress |
| 40 mm 4 Ω 2 W speaker, 5 mm thick | Ordered — AliExpress (ETA ~Nov 20) |
| WS2812B LED module (1 of the 10-pack) | Ordered — AliExpress |
| Magnetic pogo connector, 2-pin, 2.54 mm, 2 A, with ears — **female half** | Ordered — Amazon |

### Controller
| Part | Status |
|---|---|
| Seeed XIAO ESP32S3 (plain, not Sense) × 2 — one with headers for the breadboard, one bare for the build | To order — DigiKey 113991114 |
| Adafruit Mini Analog Thumbstick, Joy-Con style (#5628) × 2 | To order — DigiKey / Adafruit |
| 3 × Kailh Choc V1 Red + MBK 1u white keycaps (5 of each bought) | Ordered — keeb.io |
| 2 × INMP441 I2S MEMS mic | Ordered — AliExpress |
| 3.7 V 1000 mAh LiPo 803040, JST-PH 2.0, protected (8 × 30 × 40 mm) | Ordered — Amazon |
| TP4056 USB-C charger module with DW01A protection | Ordered / to order — Amazon |
| SS12D00G3 slide switch, 3 mm handle | Ordered — AliExpress |
| WS2812B LED (2nd of the 10-pack) | Ordered |
| Magnetic pogo connector — **male half** | Ordered — Amazon |
| 6 × 2 mm neodymium magnets | To order — Amazon (hold the controller on the dock) |
| 2 × 100 kΩ resistors (battery voltage divider) | **To order** — resistor assortment |

### Shared / tools
28 AWG silicone wire, M2 heat-set inserts + M2 screws, PETG filament, soldering station kit (iron, flux, helping hands, solder, sucker), multimeter, breadboards + jumper wires, 2.54 mm breakaway headers, USB-C data cable to the Mac.

### Not used in rev 2 (cancel if not shipped, otherwise spares)
PS2 joystick modules, EC11 encoders, 10 mm brass hinges, NRF24L01 (if ordered), Pololu S7V8F3 (if ordered), 8 Ω 1 W speaker (if it arrives).

---

## 4. Pin maps

### Dock — ESP32-S3 N16R8 DevKitC-1
Pins to keep free:
- **GPIO35/36/37:** octal PSRAM.
- **GPIO19/20:** native USB, which is Path B.
- **GPIO0/3/45/46:** strapping pins.
- **GPIO38 and 48:** the onboard RGB LED is on one of them, depending on board revision.
- **GPIO43/44:** debug UART.

```
DISPLAY  ST7796S (SPI2)     MOSI GPIO11   SCLK GPIO12   CS GPIO10
                            DC   GPIO9    RST  GPIO14   BL (PWM, LEDC) GPIO8
TOUCH    FT6336U (I2C)      SDA  GPIO1    SCL  GPIO2    INT GPIO4
AMP      MAX98357A (I2S0)   BCLK GPIO15   LRC  GPIO16   DIN GPIO17   SD_MODE → 3V3   VIN → 5V
LED      WS2812B            DIN  GPIO21                               VDD → 5V
POGO     5V out             pogo + ← 5V (VBUS)   pogo − ← GND
DOCKED?  pogo current sense (optional)  GPIO5 (ADC1) via divider
USB      native USB-C port  GPIO19/20 (Path B data + power)
FREE     GPIO6, 7, 13, 18, 39, 40, 41, 42, 47
```
Plug the Mac into the DevKitC's **native USB** port, not the UART/COM port, for Path B. Flashing works through either port.

### Controller — Seeed XIAO ESP32S3 (all 11 pins used)
```
D0  GPIO1   Stick X        (ADC1)
D1  GPIO2   Stick Y        (ADC1)
D2  GPIO3   Battery sense  (ADC1, from 100k/100k divider on switched battery +)
D3  GPIO4   Key 1 — Cancel (INPUT_PULLUP, to GND)
D4  GPIO5   Key 2 — Voice  (INPUT_PULLUP, to GND)
D5  GPIO6   Key 3 — Send   (INPUT_PULLUP, to GND)
D6  GPIO43  Status LED     (WS2812B data; may blink once at boot, harmless)
D7  GPIO44  Stick click    (INPUT_PULLUP, to GND)
D8  GPIO7   I2S BCK  ─┐
D9  GPIO8   I2S WS   ─┼─ both INMP441 share these 3 wires
D10 GPIO9   I2S SD   ─┘  mic A L/R → GND (left), mic B L/R → 3V3 (right) = one stereo stream
```
Stick X/Y use ADC1 on purpose: ADC2 stops working while Wi-Fi is on.

### Controller power
```
pogo + / − ──► TP4056 IN+ / IN−
LiPo ────────► TP4056 B+ / B−
TP4056 OUT+ ─► slide switch ─► XIAO BAT+ pad ─┬─► 100k ─┬─► 100k ─► GND
TP4056 OUT− ─────────────────► XIAO BAT− pad  │         └─► D2 (battery sense)
```
**Rule:** slide switch **OFF** whenever the XIAO's own USB-C is plugged in for flashing. Otherwise the XIAO's charger and the TP4056 would both charge the same cell.

The TP4056 module charges at 1 A, which is 1C for this cell. To go gentler, swap its PROG resistor (1.2 kΩ, usually labeled R3) for 2.4 kΩ, which gives about 500 mA.

---

## 5. Protocol (same over Wi-Fi, USB and ESP-NOW)

The JSON messages from rev 1 stay; this revision adds source, session and audio messages.
- **Over USB serial:** one JSON object per line.
- **Audio over ESP-NOW and USB:** small binary frames with a 4-byte header (type, sequence, length), so audio doesn't pay JSON overhead.

```jsonc
// Controller/Dock → Mac
{ "t": "hello", "dev": "dock" | "controller", "fw": "0.2.0", "path": "wifi" | "usb" }
{ "t": "input", "src": "controller", "key": "voice" | "send" | "cancel" | "click", "ev": "down" | "up" }
{ "t": "stick", "dir": "up" | "down" | "left" | "right" | "center", "ts": 123456 }
{ "t": "audio_start", "rate": 16000, "ch": 1, "codec": "pcm16" | "adpcm" }
//   …binary audio frames…
{ "t": "audio_end" }
{ "t": "batt", "mv": 3910, "charging": true }
{ "t": "ping", "ts": 123456 }

// Mac → Dock (screen) / Controller (LED, haptics later)
{ "t": "sessions", "items": [ { "id": "cc-1", "app": "claude-code", "name": "projects", "status": "working" | "waiting" | "done" | "error", "last": "Editing auth.ts" } ] }
{ "t": "approval", "id": "cc-1", "prompt": "Allow edit to auth.ts?", "options": ["Reject", "Approve", "Approve for session"] }
{ "t": "transcript", "text": "…", "final": false }
{ "t": "usage", "api_usd": 12.4, "five_hour_pct": 38, "week_pct": 4 }
{ "t": "led", "color": "amber", "mode": "pulse" }
{ "t": "sound", "name": "waiting" }
{ "t": "pong", "ts": 123456, "mac_ts": 987654 }
```
Audio: 16 kHz, 16-bit. The controller mixes its two mics to mono before sending. Over ESP-NOW it uses IMA-ADPCM (4:1, about 64 kbit/s) so the stream fits comfortably; over Wi-Fi it can send raw PCM.

---

## 6. Voice pipeline (our own "Wispr Flow")

All of it lives in the companion app. It's local by default; cloud is used only where you choose it.

```
hold VOICE ─► mic stream ─► VAD trim ─► speech-to-text ─► cleanup LLM ─► router ─► SEND / CANCEL
                                            ▲                 ▲              │
                                   custom vocabulary   dictionary + context  ├─► paste into the focused app
                                                                             ├─► selected agent session (prompt)
                                                                             └─► to-do list
```

| Stage | v0 choice | Notes |
|---|---|---|
| Capture | Hold Voice to record; release to stop | Target under 100 ms from press to recording. The controller keeps the I2S clock warm while awake so the first word isn't clipped. |
| Voice activity detection (VAD) | Silero VAD or WebRTC VAD | Trims silence so speech-to-text gets less audio and finishes faster |
| Speech-to-text | **Local Whisper on the M4:** whisper.cpp, MLX-Whisper or faster-whisper with a large-v3-turbo-class model | Private and free. **Groq Whisper** is the cloud fallback (and also for the Windows laptop). Both are passed the custom vocabulary as a prompt. |
| Cleanup | A fast Claude model through the API | Removes fillers, fixes punctuation and formatting, keeps your wording. Mode-aware: **prompt** (precise), **message** (natural), **email** (polished). |
| Dictionary | `voice/dictionary.yaml`: names, brands, projects, tech terms, with common mis-hearings mapped to the right spelling | Grow it by voice ("add … to my dictionary"). Later: learn automatically when you edit a pasted transcript. |
| Context | The frontmost app, plus the selected agent session and its project folder | Picks the mode and tone, and resolves "this file" or "that function" |
| Edit by voice | After a transcript appears, hold Voice again and say the change ("change Tuesday to Thursday") | The cleanup LLM edits the pending text instead of appending |
| Output | **Send** delivers it; **Cancel** throws it away | Text shows on the dock first, so nothing goes out unseen |
| Delivery | macOS: clipboard + Cmd-V via Accessibility (the previous clipboard is restored). Windows: SendInput. Agent sessions: written to the session's input. | macOS asks once for Microphone and Accessibility permission |

**Latency targets (to measure):**
- Press → recording: under 100 ms.
- Release → cleaned text on the dock: under 1.5 s for a sentence.
- Send → text in the app: under 200 ms.

**Prior art to borrow from (MIT, read the code, don't copy closed apps):** FreeFlow, OpenWhispr, VoiceInk, Handy.

---

## 7. Platform plug-in plan

Each platform is one plug-in file in `companion-app/platforms/`. A plug-in declares what it can do; the dock UI only shows actions a plug-in supports.

```python
class Platform:
    name: str
    caps: set[str]          # subset of {"status", "approve", "prompt", "focus"}
    def sessions(self) -> list[Session]: ...         # for "status"
    def on_event(self, cb) -> None: ...              # push status changes
    def approve(self, session_id, choice) -> None: ...
    def send_prompt(self, session_id, text) -> None: ...
    def focus(self, session_id) -> None: ...         # bring its window/tab to the front
```

| Plug-in | How it connects | status | approve | prompt | focus | Order |
|---|---|---|---|---|---|---|
| **Claude Code** (CLI) | Claude Code **hooks** call a tiny script that posts to the companion app on localhost: Notification → WAITING, Stop → DONE. The PreToolUse / permission hook *blocks* until you press Approve or Reject on the device, then returns the decision. Running sessions are also tracked through `stream-json`. | ✅ | ✅ | ✅ | ✅ | 1st |
| **Generic app** | Brings any app to the front by name, then pastes text. Used as the base for every chat and cloud app below. | — | — | ✅ | ✅ | 1st |
| **Cursor** (free) | Cursor hooks for start/stop events; prompt by focusing the chat box and pasting. Cursor doesn't yet expose "waiting for approval" (open feature request); investigate its local state, see below. | partial | later | ✅ | ✅ | 2nd |
| **Codex CLI** | `notify` config runs a script on turn complete → DONE; prompt and approvals through the session (to verify against current Codex docs) | partial | later | ✅ | ✅ | 3rd, if used |
| **Claude** (desktop / claude.ai), **ChatGPT**, **Grok** | Generic app + per-app shortcuts (e.g. start a new chat) | — | — | ✅ | ✅ | 2nd |
| **Claude Duet** | Lives on phone and claude.ai; no public status API yet. Voice into claude.ai. | when an API appears | — | ✅ | ✅ | watch |
| **ChatGPT Dots** | Inside ChatGPT (Pro plan); no public API announced. Voice into ChatGPT. | when an API appears | — | ✅ | ✅ | watch |
| **Grok Bot** | Mac app (beta: SuperGrok Heavy or Cursor Ultra/Teams) | when an API appears | — | ✅ | ✅ | watch |
| **Meta Muse** | Phone, WhatsApp, muse.ai; no desktop app | — | — | ✅ (web) | ✅ (web) | watch |

**The joystick across platforms:** left/right switches between sessions and apps in one list. Claude Code sessions, Cursor, then pinned chat apps. Up/down scrolls; click opens or focuses.

**Using REA (Reverse Engineer Anything):** only for **interoperability** with apps you use, such as finding where Cursor keeps its agent state so we can show WAITING. Check each app's terms first. It is not for copying closed apps like Wispr Flow; we build our voice pipeline from the open-source projects above.

---

## 8. Firmware layout (Arduino framework, two targets)

```
firmware/
  common/protocol.h       message types, binary audio frame header
  dock/                   ESP32-S3 N16R8
    dock.ino
    display.*             LVGL 9, ST7796 (LV_COLOR_16_SWAP 0; start SPI at 20 MHz, then 40)
    touch.*               FT6336U
    transport_usb.*       USB CDC (native port), line-delimited JSON
    transport_wifi.*      WebSocket client
    espnow_bridge.*       controller ⇄ dock relay (Path B)
    audio_out.*           MAX98357A, alert sounds
    led.* power.*
  controller/             XIAO ESP32S3
    controller.ino
    input.*               keys, stick (deadband, flick detection), click
    mic.*                 I2S stereo in → mono mix → PCM / IMA-ADPCM
    transport_wifi.*      Path A
    transport_espnow.*    Path B
    battery.* led.* sleep.*   light sleep between presses; wake on any key
```
Use ESP-IDF's new I2S channel driver (`i2s_chan_handle_t`). The dock only plays audio and the controller only records, so the rev 1 "two peripherals on shared pins" problem goes away.

---

## 9. Build sequence

| Week | Work | Pass when |
|---|---|---|
| 1 | Dock on the breadboard: display + touch, LVGL session list with fake data, USB CDC link + Wi-Fi link to the companion app | Screen updates from the Mac over **both** paths |
| 1–2 | Controller on the breadboard (XIAO with headers): keys, stick, LED, battery sense | Key and stick events reach the Mac over both paths |
| 2 | Claude Code plug-in: hooks for WAITING/DONE, approvals from the device | Approve a real Claude Code tool call from the device, 10/10 |
| 2–3 | Mics + voice pipeline: local Whisper, cleanup, dictionary, Send/Cancel, paste anywhere | Dictate into Claude, ChatGPT and Cursor; agent prompt by voice works |
| 3 | **Latency + battery shoot-out** (below) → pick the default path | Numbers recorded |
| 3–4 | Measure every part with calipers → CAD dock + controller → print → assemble | Fully assembled, docks and charges |
| 4 | Generic app + Cursor plug-ins, alert sounds, Work Brief screen | Test plan passes |

### Path A vs Path B shoot-out
Run each test 50 times per path, recording the median and 95th percentile.
1. **Key press → event at the Mac.** The device timestamps the press; the clock offset is estimated from ping/pong round trips.
2. **Voice key → first audio frame at the Mac.**
3. **Release → cleaned text on the dock.**
4. **Mac update → pixels on the dock.** The Mac sends a frame-counter screen; filmed at 240 fps on the iPhone.
5. **Dropouts:** audio frames lost per minute.
6. **Controller battery:** idle hours and talk-time hours from a full charge, per path.

---

## 10. Test plan

| Test | Pass condition |
|---|---|
| Display | Session list at ≥ 25 fps while streaming audio |
| Inputs | 3 keys, click and 4 stick directions register 20/20, no ghost flicks |
| Approvals | Claude Code approve/reject from the device 10/10; no approval possible while disconnected |
| Voice | 10-word sentence correct ≥ 9/10 including your own terms; Send/Cancel always respected |
| Latency | Meets the section 6 targets on the chosen path |
| Reconnect | Unplug/replug USB or drop Wi-Fi → back within 5 s |
| Docking | Controller seats magnetically, starts charging every time (20/20) |
| Battery | Controller lasts a full workday off the dock (target 8 h mixed use) |
| Comfort | 10 minutes handheld without discomfort |

---

## 11. Shell (to redo in CAD after parts arrive)

- **Dock:** low base with a speaker grille; display on a printed fold-flat hinge at the back; front tray where the controller lies flush with the female pogo pins centered and magnets on each side; USB-C at the back.
- **Controller bar:** about 90–95 mm long, sized to the Choc keys plus the stick block.
  - Keys at 19 mm pitch.
  - Stick in a round recess, with a printed flat wide cap and four direction ticks.
  - Mic grilles and a foam gasket on the stick end face.
  - LED light pipe next to the stick.
  - Battery under the keys.
  - Male pogo pins and magnets on the docking edge.
  - Slide switch on the side.
  - XIAO's U.FL antenna placed away from the battery.
- **Dock width:** the display module is 108 mm wide, so the dock will be about 115–120 mm wide (SlashVibe's is 105 mm).
- The clamshell `shell.py` is retired. The new script reuses its fit-check approach.

---

## 12. Open questions
1. Default transport after the shoot-out. USB is expected to win on latency; Wi-Fi stays as the room-range fallback.
2. Local Whisper model size vs speed on the M4; when to fall back to Groq.
3. Cursor "waiting for approval": wait for a hook, or read Cursor's local state (REA research)?
4. Do the cloud agents (Duet, Dots, Grok Bot, Muse) publish status APIs? Re-check monthly.
5. Approvals: Claude Code hooks (preferred) vs the PTY wrapper from rev 1. The hooks route needs no PTY.
6. Battery life on Path A vs B; whether to make Path B the controller's default.
7. Companion app auto-start on Mac (launchd) and Windows (Task Scheduler).

## 13. v1 after v0 passes
- Machined aluminum shell (from the v0 print as reference).
- Custom PCBs for dock and controller.
- Lower-profile switches.
- Menu-bar companion app.
- Open SDK so other tools can draw screens and receive button events (SlashVibe's SDK model: Node/Python on the computer, UI streamed to the device).
