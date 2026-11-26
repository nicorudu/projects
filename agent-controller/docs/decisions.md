# Decision log

One line per decision: what, why, and what it replaced. Newest first.

| Date | Decision | Why | Replaces |
|---|---|---|---|
| 2026-11-26 | READY = a session open at its prompt with nothing asked yet; IDLE = DONE or READY with no activity for 10 minutes | The reference shows both words without explaining them; this keeps the list honest about what is fresh | Drop READY and keep only IDLE |
| 2026-11-26 | The Home selection follows its session, not a row number | With focus-follows-selection on, the highlight must not slide onto another session when rows reorder | Row-number selection |
| 2026-11-26 | Protocol input `click` removed, `green` added (M1b) | The reference's stick has no click; only Send confirms an approval | Keep `click` as an alias |
| 2026-11-19 | One XIAO, not two: the spare ESP32-S3 dev board stands in for the controller on the breadboard, and the XIAO goes into the build bare | Nico already has a second ESP32-S3 board on order; same chip, same firmware, different pin table | Two XIAO boards (one with headers, one bare) |
| 2026-11-18 | A fixed-tilt screen (rev 3b) is mocked up as an option; the folding lid stays the plan until Nico chooses | It removes the hinge, the flexing wires and the pin bending, but it can't close and departs from the reference | — |
| 2026-11-18 | The lid is 13 mm thick, and the display's pins are bent flat (Nico's choice) | The pins are about 8 mm tall and a 10 mm lid had 1.3 mm behind the display; bending avoids desoldering 14 pins | 10 mm lid with the header removed |
| 2026-11-18 | Part placement fixed by a 3D concept model with an automatic overlap check: dock board on the right of the base, battery under the Send and Voice switches, XIAO and charger at the left end, dock status light in the base top | The x-ray views show every part in place and the check proves nothing collides | Placement described in words only |
| 2026-11-18 | The pivot sits 4 mm in from the front face with a 12 mm knuckle; the Voice plate is notched around it | The block must clear the key section through the whole 90° swing | Pivot position left open |
| 2026-11-18 | The battery connects through a JST-PH pigtail, and a 0.1 µF capacitor sits on the battery-reading pin | Nothing is soldered to a live battery; the high-resistance divider reads steadily | Soldering the battery leads; no capacitor |
| 2026-11-18 | The controller gets its own breadboard, and the dock's current is measured with a USB-C power meter | The dock stays wired while the controller is built; charging current through the dock must be measured, not guessed | Sharing the kit breadboards; multimeter only |
| 2026-11-18 | The joystick block pivots 90° on a hollow printed pin, with the wires through the pin | The reference does this (Nico's photo, brand film, teardown). The Nov 11 "no swivel" decision was wrong. | Rigid bar |
| 2026-11-18 | Key order is Cancel / Send / Voice, with Voice beside the joystick | Photos of real units | Cancel / Voice / Send |
| 2026-11-18 | Keys are large printed plates on Choc switches, hinged at the rear edge | Matches the reference's look; a big plate on one switch would tilt otherwise | 1u keycaps |
| 2026-11-18 | The stick click is unused; right opens, left goes back, only Send confirms an approval | The reference stick has no click; a stray flick must never approve anything | Click to open and confirm |
| 2026-11-18 | A green button on the joystick block, sharing one analog pin with the pivot sensor | The reference has it; the XIAO has no spare pin | LED only |
| 2026-11-18 | The controller attaches to the base's front face; no tray | Reference layout; a tray would block the pivot | Tray in the dock |
| 2026-11-18 | The controller only talks to the dock (ESP-NOW); USB vs Wi-Fi is compared on the dock's link | Same as the reference; better battery; less firmware | Controller also on Wi-Fi |
| 2026-11-18 | The controller senses "block swung out" and "docked" and remaps stick directions itself | Stick directions must match what the user sees in all three positions | No position sensing |
| 2026-11-18 | Screens stay templates filled by small messages; no streamed pictures | Fast on our hardware; the reference streams its interface from the computer | — |
| 2026-11-18 | Learn from SlashVibe's open-source release but don't copy its code | It will be AGPL-3.0, which would force that license on our code | — |
| 2026-11-12 | Voice engine is Wispr Faux (Nico's own dictation app), not a new Whisper pipeline in the companion | Already more accurate and polished; one engine on Mac and Windows | mlx-whisper / Groq + Claude cleanup in the companion |
| 2026-11-12 | Voice flow: text shows on the dock first; Send delivers, Cancel discards | Avoids mistakes; matches SlashVibe | — |
| 2026-11-12 | The control link goes into a copy of Wispr Faux inside this project; the wispr-faux repo is never edited | Keep Nico's working app safe | Editing wispr-faux directly |
| 2026-11-11 | All Claude Code hooks are command hooks running `companion.hooks.report` (async for status, blocking for approvals) | Claude Code's `http` hooks print "hook error" lines whenever the app is off; the script stays silent | HTTP hooks |
| 2026-11-11 | Device and terminal both answer approvals; the first answer wins, and the device clears when the session moves on | In interactive mode Claude Code shows its own menu while our hook waits (Mac Mini test) | Device-only answer |
| 2026-11-11 | "Approve for session" applies only `addRules` / `addDirectories` suggestions | Applying a `setMode` suggestion switched Claude Code to accept-edits (Mac Mini test) | All suggestions |
| 2026-11-11 | Approval screen has 4 options: Approve / Approve for session / Reject / Ask in terminal | Claude Code's terminal waits while our hook is open, so there must be a way to hand the question back | 3 options |
| 2026-11-11 | Approvals time out after 120 s to Claude Code's own prompt | A forgotten approval must never stall a session | — |
| 2026-11-11 | "Approve for session" applies Claude Code's suggested rules with `destination: "session"` | Same convenience as the terminal's option, without writing rules into settings files | — |
| 2026-11-11 | `SessionStart` uses an async command hook (`companion.hooks.report`); all other events use HTTP hooks | Claude Code only allows command hooks on `SessionStart`; the script also captures the terminal tab for focus | All HTTP |
| 2026-11-11 | Managed sessions no longer use `--dangerously-skip-permissions` | Approvals now go through the device; unanswered requests in `-p` mode are denied by Claude Code | v0 `main.py` |
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
