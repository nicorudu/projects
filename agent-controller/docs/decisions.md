# Decision log

One line per decision: what, why, and what it replaced. Newest first.

| Date | Decision | Why | Replaces |
|---|---|---|---|
| 2026-11-11 | Firmware built with PlatformIO, not the Arduino IDE | Two boards plus a desktop UI simulator in one project, pinned library versions, buildable from the command line | Arduino IDE |
| 2026-11-11 | Dock screens are fixed LVGL templates filled by `view` messages from the Mac | Keeps firmware small; all logic stays in the companion app | — |
| 2026-11-11 | Claude Code integration through HTTP hooks (`PermissionRequest` for approvals) | No terminal wrapper; safe fallback to the normal prompt when the device is off | PTY wrapper / `--dangerously-skip-permissions` |
| 2026-11-11 | Build the software against a fake device and a UI simulator before hardware arrives | Most of the work isn't blocked on parts | — |
| 2026-11-11 | Approvals through Claude Code hooks, not a PTY wrapper | Hooks can block and wait for the device's answer; simpler and brings approvals into v0 | PTY approval flow deferred to v1 |
| 2026-11-11 | Build both USB and Wi-Fi data paths and measure them | USB should be faster and steadier for voice; Wi-Fi gives room range | Wi-Fi only |
| 2026-11-11 | Controller is one rigid bar (keys + stick end); "rotate" means turning the whole bar | Matches SlashVibe's spec drawing; no pivot or wires through a pivot | Swiveling joystick pod |
| 2026-11-11 | Keys are Cancel / Voice / Send; approvals are chosen on screen | Matches the reference product's interaction | Approve / back / mic keys |
| 2026-11-11 | Own voice pipeline: local Whisper + Claude cleanup + personal dictionary | Understands Nico's vocabulary; private; no dictation subscription | Third-party dictation |
| 2026-11-11 | Moved I2S off GPIO35–37 and display RST off GPIO3 | GPIO35–37 are used by the N16R8's octal PSRAM; GPIO3 is a strapping pin | Rev 1 pin map |
| 2026-11-09 | Desk dock + detachable controller | Closer to the final v1; the mic belongs on the handheld part | Clamshell |
| 2026-11-09 | Joy-Con-style low-profile stick (Adafruit #5628) | The PS2 stick forced a 24 mm-thick base | PS2 joystick module |
| 2026-11-09 | Second ESP32 (XIAO ESP32S3) in the controller | A detachable controller needs its own processor, battery and charger | Single ESP32 |
| 2026-11-08 | Wi-Fi WebSocket to a Python companion app on the Mac | The computer does the heavy work; the device stays a thin client | — |
| 2026-11-08 | ESP32-S3 N16R8 (8 MB PSRAM) for the dock | LVGL, networking and audio together need PSRAM | — |
