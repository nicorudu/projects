# Handoff — AI Agent Controller

**Read this first when picking the project back up** (new chat, after a context reset, or switching to the Mac Mini). It holds the current state, the next step, and the rules. It is updated and pushed after every step.

Last updated: 2026-11-26 · by Claude (Claude Code on the Mac Mini)

---

## 1. Where we are right now
- **Rev 3 (2026-11-18): the plan and blueprint were rebuilt** after re-checking every photo in the chat and everything public about SlashVibe. Where older notes disagree, rev 3 wins.
  - Read in this order: [plan](docs/plan.md) → [blueprint rev 3](docs/agent-controller-v0-blueprint.md) → [reference notes](docs/research/slashvibe-reference.md).
  - **Biggest correction: the joystick block pivots 90°.** The Nov 11 notes said it didn't. Nico's photo and the brand film show it does.
  - Also changed:
    - Key order is Cancel / Send / Voice.
    - Keys are large printed plates.
    - The stick click is unused.
    - A green button is added on the block.
    - The controller attaches to the base's front face (no tray).
    - The controller only talks to the dock.
  - **No hardware is wasted.** One new part (C10 tactile buttons) and a few "check you have it" items; see plan §6.
  - **Shopping list (current): [hardware/bom/shopping-list-2026-11-19.md](hardware/bom/shopping-list-2026-11-19.md).** It is checked against Nico's order screenshots. Still to buy: resistor kit (C9), tactile buttons (C10), JST-PH pigtails (C11), capacitor kit (C12), USB-C power meter (T8). **The list now names one exact product and quantity per line** (Nico orders exactly what is written; never give him a generic spec). Nico confirmed in chat that the thumbstick and breadboards with jumpers are ordered. **One XIAO is enough:** the spare ESP32-S3 board (X7) stands in for the controller on the breadboard. Nothing is confirmed as arrived yet.
  - Layout drawing: `hardware/renders/2026-11-18-rev3-layout/rev3-layout.png`.
  - **Concept model (3D):** `hardware/cad/rev3-pivot/concept.py` → renders in `hardware/renders/2026-11-18-rev3-concept/` (finished look, x-ray, exploded). Its overlap check passes. Part placement and the tight spots are in blueprint §4.7. The lid is 13 mm thick (decided), so the device is about 35 mm tall closed.
  - **The app's controls match rev 3 since M1b (2026-11-26).** See the M1b line below.
- **PR #9 is merged** (2026-11-18): rev 3, the shopping list and the M2 plan from PR #7 are all on `main`.
- **PR #10 is merged** (concept models, renders, fixed-tilt option).
- **Website:** checked 2026-11-18. nicorudu.com doesn't list this project yet. Nico's website chat adds it; the text to hand over is in §6.
- **Open choice: folding lid or fixed tilt.** Nico asked for a mock-up of a screen that is always tilted. It is done as rev 3b: [docs/option-fixed-tilt.md](docs/option-fixed-tilt.md), model in `hardware/cad/rev3b-fixed-tilt/`, renders in `hardware/renders/2026-11-18-rev3b-fixed-tilt/`. The folding lid stays the plan until he chooses.
- **M1b is done and checked on the Mac Mini (2026-11-26, PR #20, 66 tests).** What changed:
  - Stick right opens the detail page; stick left, Cancel and the green button go back. No filters, no stick click.
  - Only Send confirms an approval. Protocol: input `click` removed, `green` added.
  - Focus follows selection: 0.6 s after the stick rests on a row, that session's window comes forward (`focus_follows_selection`, on by default).
  - The highlight stays on its session when rows reorder.
  - Status words READY and IDLE added (meanings are ours; see docs/decisions.md). The detail page has "Worked for 6m 24s" and the whole last message, scrollable.
  - Fake device keys: arrows, `s` Send, `c` Cancel, `v` Voice, `g` green. **Enter no longer does anything.**
  - **Nico's check on the Mac Mini passed** with real Claude Code sessions (all five steps; §8). Focus-follow stays on.
- **M3 is built (2026-11-26, branch `agent-controller-m3-screens`).** The screens are one LVGL library, `firmware/lib/AgentUI`, compiled by both the simulator and the dock.
  - Simulator: `cd firmware/sim && make`, then `python tools/sim_bridge.py` with the app running. Pictures of every screen: `make snapshots` → `firmware/sim/snapshots/`.
  - Screens: Agents, Detail, Approval, Voice (layout only), Connecting, plus a toast and a Disconnected banner.
  - The same library compiles for the dock board (`firmware/bench/dock_ui`, 665 kB). **Not run on the real display yet.**
  - **Toolchain decision (Nico): arduino-cli for the boards, a Makefile for the simulator.** PlatformIO is dropped.
  - New protocol message from screen devices: `layout` (how far the detail page scrolls). 67 tests.
  - **Open: Nico's look-over in the simulator** (§6, "M3 look-over"), including whether the look is close enough to the reference.
  - Known limits: fonts are ASCII only (accents dropped, emoji shown as `?`); Voice has no engine until M2; the READY color is still a proposal.
- **Next step:** Nico's M3 look-over, then the display test on the bench when the jumpers arrive (about 2026-11-28), then `dock_ui` on the real display. **Parts arrived 2026-11-26** (all but a spare XIAO), so M4 (dock on the breadboard) starts now, alongside M1b. **M4 bench start is done (2026-11-26):** the dock board is a real N16R8 (16 MB flash, 8 MB PSRAM) and the Mac Mini can build and flash it. **Next on the bench: the display** (blueprint §11). The display test is written and compiles (`firmware/bench/dock_display/`, wiring table in its README) but is **not flashed**: the jumper wires arrive about 2026-11-28.
- **Waiting on Nico:** the four decisions in plan §8. The first is which parts were ordered and which have arrived.
- **Done:** M0 and M1, merged to `main` (PR #3). 45 tests pass, on the Mac Mini too (Python 3.14.7, after a test-race fix on branch `agent-controller-mac-mini-test`).
  - M1 was **verified live** twice: real Claude Code 2.1.322 in the cloud workspace (hook → fake device Approve → the command ran), then the full §6 test on the Mac Mini.
- **Mac Mini test — done 2026-11-11.** Hooks are installed on the Mac Mini (venv at `software/companion-app/.venv`). Note: Claude Code's auto mode won't let Claude run `install-hooks` / `uninstall-hooks` (it edits Claude's own `~/.claude/settings.json`), so Nico runs those.
  - **Works:**
    - Status on the fake device (working / waiting / done, LED).
    - Approve: C's own menu closed by itself; C showed "Allowed by PermissionRequest hook".
    - Reject (`c`): "Denied by PermissionRequest hook"; Claude didn't retry.
    - Ask in terminal (↑ Enter; ↑ `s` since M1b): B said "Answer in the terminal", C's menu answered normally, the row went to done.
    - Send (`s`): C became the active window, with no macOS permission prompt.
    - A curl straight to the hook server.
  - **Three issues found — fixed by the cloud session on branch `agent-controller-hook-fixes` (54 tests, verified live in the cloud against real Claude Code):**
    1. **Approve for session changed the permission mode.** C switched to "accept edits on" because we applied *all* `permission_suggestions`, and they included a `setMode` change. **Fix:** only `addRules` and `addDirectories` suggestions are applied, always with `destination: "session"`. If nothing is left, it's a plain allow.
    2. **Terminal menu and hook run at the same time.** In interactive mode, Claude Code shows its own menu while our hook is open, and the first answer wins. Answering in C left a stale Approval screen on B until the 2-minute timeout. **Fix:** the question is cleared ("Answered in the terminal") as soon as that session moves past it: the same tool finishes (`PostToolUse` / `PostToolUseFailure` with the same tool and input), or the turn ends (`Stop`, `StopFailure`, `UserPromptSubmit`, `SessionEnd`). Events that fired *before* the question don't count (`_ts` comparison), and a different tool finishing doesn't count either, because tools can run in parallel.
    3. **Hook errors with the app off.** C printed `hook error: connect ECONNREFUSED 127.0.0.1:8766` on every event. **Fix:** no more `http` hooks. Every hook runs `python -m companion.hooks.report`, which is always silent.
       - Status events are `async` command hooks, so Claude Code never waits for them. They carry `_ts`, so out-of-order arrivals are ignored.
       - `PermissionRequest` is a blocking command hook with `--wait`. It prints the decision, or nothing (= normal prompt).
       - Verified in the cloud: with the app off, every hook exits 0 with empty stderr, and there are 0 error lines.
       - **Nico must re-run `python -m companion install-hooks` once on the Mac Mini.** It replaces the old http hooks; there are now 10 hooks, because `PostToolUseFailure` was added.
  - Also fixed on the Mac Mini: a test race in `test_approve` (see step log).
- **M1 is fully done.** PRs #4 and #5 are merged, and the hook fixes were rechecked on the Mac Mini on 2026-11-11:
  - 54 tests pass and 10 hooks are installed.
  - Answering in the terminal clears the device ("Answered in the terminal").
  - Approve for session keeps `manual mode on`.
  - With the app off: the normal menu appears and there are **no hook error lines**.
- **Mac Mini state:** the repo is on `main`, the hooks are installed (10, command type), and the venv is at `software/companion-app/.venv`. Test files `~/agent-controller-test-*.txt` can be deleted.
- **M2 (voice): planned, tabled 2026-11-12 at Nico's request.** Don't start it until he says so.
  - **Voice engine = Wispr Faux, Nico's own dictation app** (`nicorudu/wispr-faux`: Swift for Mac, C#/.NET for Windows; on-device Whisper large-v3 turbo, stumble cleanup with a guard, clipboard-safe paste). The companion app doesn't get its own Whisper pipeline.
  - **Rule: never edit the `nicorudu/wispr-faux` repo directly.** The control link goes into a copy of Wispr Faux inside this project (`software/wispr-faux-controller/`, app name "Wispr Faux Controller", its own bundle ID).
    - A stray branch `control-link-spec` was pushed there by mistake on 2026-11-12. Nico deletes it at github.com/nicorudu/wispr-faux/branches; the cloud session can't delete branches.
  - **UX (decided):** the Voice key → Wispr Faux transcribes → the text shows on the dock's Voice review screen → **Send** delivers it, **Cancel** discards it. As close to SlashVibe as possible.
  - **Delivery (proposed):** the stick ←/→ on the review screen picks where Send goes: the app in front (paste), or a Claude Code session (focus its tab, paste, Return).
  - **Order:** Mac first, then Windows.
  - **Link spec draft:** [docs/wispr-faux-control-link.md](docs/wispr-faux-control-link.md) (loopback WebSocket, token + Origin check, listen/stop/cancel, external audio for the controller mics, insert with Return).
  - **Open question:** does the copy *replace* the original on the Mac (one app: hotkey + controller), or run *side by side* (no hotkey, ~1–2 GB more memory, possible 2-minute model reloads)?
  - **Work split:** spec + companion side in the cloud; the Swift build and test with Claude Code on the Mac Mini (needs Xcode).
- **M1 design notes (from the hooks docs, rechecked 2026-11-11):**
  - `SessionStart` accepts only command hooks. We use an async command hook that runs `python -m companion.hooks.report`, which posts the event plus the terminal app and TTY.
  - ~~All other events are `http` hooks.~~ **Since the hook fixes:** every event uses the same command hook (`companion.hooks.report`). Status events are async; `PermissionRequest` waits (`--wait`, 600 s hook timeout). The app answers within `approval_timeout_s` (120 s), or gives no decision.
  - The Approval screen has 4 options: Approve / Approve for session / Reject / Ask in terminal (= no decision → normal prompt).
  - ~~While a `PermissionRequest` hook is open, the terminal waits.~~ **Wrong (Mac Mini test):** in interactive mode the terminal shows its own menu at the same time, and the first answer wins (issue 2 above).
  - "Approve for session" = `allow` + `updatedPermissions` = the request's `addRules` / `addDirectories` suggestions with `destination: "session"` (never `setMode`; issue 1 above).
  - Hook server checks: loopback only, `Host` must be localhost/127.0.0.1, and the body must be JSON (blocks browser cross-site posts).
  - A refused connection on an `http` hook **does** print a "hook error" line in Claude Code (checked on the Mac Mini). That's why every hook is now a command hook that stays silent (issue 3 above).
- **Code map (M0 + M1):**
  - `software/companion-app/companion/`
    - `core/app.py`: state reducers, inputs, render loop, heartbeat watchdog.
    - `core/state.py`, `core/intents.py`.
    - `view/builder.py`: view / patch / LED.
    - `protocol/`: messages and COBS framing.
    - `transports/websocket.py`.
    - `devices/link.py`.
    - `platforms/claude_code/attached.py`: hooks → status and approvals.
    - `platforms/claude_code/managed.py`: `claude -p` stream.
    - `hooks/server.py`, `hooks/install.py`, `hooks/report.py`.
    - `osx/focus.py`.
    - `__main__.py`: `run` / `install-hooks` / `uninstall-hooks` / `doctor`.
  - `tools/fake_device.py`.
  - Tests in `software/companion-app/tests/`.

## 2. Milestones

Full table with pass conditions: [plan §5](docs/plan.md).

| # | What | Needs parts? | State |
|---|---|---|---|
| M0 | Package restructure, protocol v1, WebSocket transport, fake device | No | **done** (2026-11-11) |
| M1 | Claude Code hooks: live status + approvals from the fake device | No | **done** (2026-11-11), tested on the Mac Mini |
| M1b | Reference controls in the app (right opens, left back, focus follows selection, green button, no stick click) | No | **done** (2026-11-26), checked on the Mac Mini |
| M2 | Voice: a copy of Wispr Faux as the engine, dock review + Send/Cancel | No (Mac Mini) | planned, tabled (see §1) |
| M3 | Screens in the desktop simulator, styled like the reference | No | **built** (2026-11-26); Nico's look-over open |
| M4 | Dock on the breadboard: display, touch, speaker, USB + Wi-Fi links | Yes | **started** (2026-11-26): board check passed; display next |
| M5 | Controller on the breadboard: keys, stick, AUX input, mics, ESP-NOW | Yes | after M4 |
| M6 | USB vs Wi-Fi speed test, battery test | Yes | after M5 |
| M7a | Measure every part with calipers | Yes | with M4 |
| M7b | Rev 3 CAD + four test prints (pivot, key plate, stick cap, hinge) | Printer | after M7a |
| M7c | Full print, wiring, assembly | Yes | after M7b |
| M8 | Polish: usage header, sounds, Work Brief, Cursor and chat apps | No | after M7c |

## 3. Standing rules (from Nico)
1. **Document everything in GitHub after every step**, and update this handoff, so nothing is lost when the chat compacts.
2. **Audit shopping lists rigorously.** Every part change goes into `hardware/bom/BOM.csv` with a status. Past misses cost real shipping time.
3. **Website (nicorudu.com):** don't edit it. Write the exact fixes for Nico to hand to his website Claude assistant.
4. **v0 should be as close to v1 as possible**, and the printed shell should look as accurate to the reference (SlashVibe) as possible. When Nico points at something in a photo, check the photo before answering.
5. **Git:** branch first, never commit to `main`. Commit author `nicorudu <nicorudu@users.noreply.github.com>`. Never put Nico's personal email in commits or external requests.
6. **Secrets** (Groq, Anthropic keys) go in the OS keychain via `keyring`, never in the repo.
7. Nico uses an **M4 Mac Mini** (main; Claude Code runs better there) and an **HP OmniBook X Flip (Windows)**. Code must run on both.

## 4. Design in one paragraph
Three bodies, like the reference. A **lid** (4" ST7796 touch screen) folds flat onto a **base** (ESP32-S3 N16R8 DevKitC, MAX98357A + 40 mm 4 Ω 2 W speaker under a ribbed top, WS2812B, USB-C out the back). A detachable **controller** attaches to the base's front face with magnets and charges through a 2-pin magnetic connector. The controller has a key section (XIAO ESP32S3, three Choc switches under large printed plates = Cancel / Send / Voice, 1000 mAh LiPo, TP4056, slide switch) and a **joystick block that pivots 90°** on a hollow pin (Adafruit #5628 stick with a wide flat cap and no click, a green button, a status LED, 2× INMP441 mics on the end face). The controller talks only to the dock over ESP-NOW. The dock talks to the computer over USB (default) or Wi-Fi; the two are timed side by side. A Python companion app does all the logic; the dock only draws the screens it's sent.

Full detail: [plan](docs/plan.md) (goal, milestones, parts checks, risks) · [blueprint rev 3](docs/agent-controller-v0-blueprint.md) (mechanical design, pin maps, power, controls, screens, tests) · [architecture](docs/architecture.md) (code layout, state, screens/keys, hooks, milestones) · [decisions](docs/decisions.md) · [build log](BUILDLOG.md).

## 5. Key technical facts (so they don't need re-researching)
- **Pins.** Dock: never use GPIO35–37 (octal PSRAM). Avoid strapping pins 0/3/45/46. Controller: all 11 XIAO pins are used. Full maps are in blueprint §5.
  - Rev 3 controller map: D0/D1 stick X/Y, D2 battery + docked sense, D3 AUX (green button + pivot sensor on a resistor ladder), D4 Voice, D5 Send, D6 LED, D7 Cancel, D8–D10 mics.
  - Ten wires cross the pivot: 3V3, GND, BAT+, stick X, stick Y, LED data, green button, mic BCK, mic WS, mic data.
- **Reference facts that drive the design** (sources in the reference notes):
  - The joystick block pivots; the stick has no click; right opens and left goes back.
  - Key order is Cancel / Send / Voice.
  - Selecting a session brings its window forward.
  - The reference uses 4 dock contacts and a green-capped button.
  - Its software will be open-sourced under AGPL-3.0, expected by mid-December 2026. Read it then; don't copy code.
- **Protocol v1.**
  - Every message has `"v":1,"t":…`. Inputs carry `seq` + `ts` and are acked.
  - Framing: WebSocket text = JSON, binary = audio. USB = COBS `[kind:u8][payload]` (1 = JSON, 2 = audio). ESP-NOW ≤ 250 B.
  - Audio header: `stream_id:u8, seq:u16, codec:u8, samples:u16`, 16 kHz mono.
  - `hello` → `welcome` handshake; heartbeat every 500 ms, link down after 2 s.
  - The dock is driven by `view` / `patch` messages.
- **Claude Code hooks** (checked against code.claude.com/docs/en/hooks on 2026-11-11):
  - The `http` hook type POSTs the event JSON to a URL. The default timeout is 600 s, and a failure is non-blocking, **but it prints a "hook error" line**, so we don't use it.
  - Command hooks get the event JSON on stdin; `"async": true` (command hooks only) runs them in the background. A `PermissionRequest` command hook answers by printing the decision JSON on stdout; empty stdout means no decision.
  - In an **interactive** session, Claude Code shows its own permission menu *while* the `PermissionRequest` hook runs, and the first answer wins. In `-p` mode there's no menu, and no decision means the call is denied.
  - `permission_suggestions` can include `setMode` (for example, switch to `acceptEdits`), `addDirectories` and `addRules` entries.
  - `PermissionRequest` input: `tool_name`, `tool_input`, `permission_suggestions`. Reply `{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}`, or `"deny"` plus `message`. Returning no decision falls back to the normal terminal prompt.
  - `Notification` has `notification_type` (`permission_prompt`, `idle_prompt`, …).
  - Common fields: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `permission_mode`.
  - Config lives in `~/.claude/settings.json` as `{"hooks":{"Event":[{"matcher":"…","hooks":[{"type":"http","url":"…"}]}]}}`.
- **Ports.** `8765` = device WebSocket. `8766` = hook server, bound to 127.0.0.1 only.
- **Workflow quirks in the cloud sessions.**
  - Open PRs with `gh api repos/nicorudu/projects/pulls -X POST …`; the GitHub MCP tool returns 404 for this repo.
  - After pushing a new branch, run `git config --add remote.origin.fetch '+refs/heads/<b>:refs/remotes/origin/<b>'`, then fetch and run `git branch -u`. Otherwise the stop hook reports "unpushed commits".

## 6. What Nico needs to do
- **Answer the four decisions in [plan §8](docs/plan.md):** parts status, the new and missing items, voice, and finish.
- **Buy the parts on the [shopping list](hardware/bom/shopping-list-2026-11-19.md)** (checked against the real orders on 2026-11-19):
  - Not ordered yet, 1 of each, exact products named in the list: C9 Geekstory 73-value resistor kit, C10 Hilitchi 6 × 6 mm tactile button kit, C11 10-pair JST-PH 2.0 pigtails, C12 500-pc ceramic capacitor kit, T8 Plugable USBC-VAMETER3. About $70.
  - Only if needed: S6 jumpers with female ends (if the breadboard kit's are all male-to-male), a spare XIAO, T6 calipers, T10 second USB-C data cable, T11 flush cutters, S7 super glue, S8 foam tape, S9 rubber feet.
  - Thumbstick: ordered at the quantity the 2026-11-18 list gave (2 × Adafruit #5628), per Nico on 2026-11-19.
  - On arrival, check: the chargers have six pads (protected kind); the screwdriver set has an H1.5 bit; the battery plug fits the C11 socket; measure both ESP32-S3 boards.
- **Website:** give your website chat this: "Add the AI Agent Controller to the Lab section. Use `agent-controller/showcase.json` in github.com/nicorudu/projects for the title, tagline, status text, images and timeline. Status text: Building: rev 3 design (pivoting joystick block); approvals work from the fake device. Credit SlashVibe as the inspiration."
- **M4 bench start (Claude Code on the Mac Mini, from 2026-11-26).** Nico moves the hands-on work to Claude Code on the Mac Mini so it can run the commands itself. One step at a time; stop after each and tell Nico what happened.
  1. Pull `main` (PR #17 has the arrivals). Firmware uses the Arduino framework (blueprint §8); nothing is written yet (`firmware/README.md`).
  2. Nico plugs the dock board (D1, ESP32-S3 DevKitC-1 N16R8) into the Mac Mini through the port marked UART or COM. Find the new port with `ls /dev/cu.*`.
  3. Install `arduino-cli` (Homebrew) and the Espressif ESP32 core. Ask Nico before installing anything.
  4. Flash a hello sketch that prints the chip, flash size and PSRAM size. Pass: 16 MB flash and 8 MB PSRAM reported. Never use GPIO35–37 (PSRAM).
  5. Log the result in §8 and BUILDLOG, commit on a branch, and open a PR. Next is the display (bench order in blueprint §11).
  - **Done 2026-11-26, all five steps (result in §8).** Facts for the next bench session:
    - Port: `/dev/cu.usbmodem5C850305191` (the board's UART/COM port, a WCH CH343 bridge). The board shows as "Unknown" in `arduino-cli board list`; that is normal.
    - Tools on the Mac Mini: `arduino-cli` 1.6.0 (Homebrew), Espressif core `esp32:esp32` 4.0.0.
    - Board settings: ESP32S3 Dev Module, Flash Size = 16 MB, PSRAM = OPI PSRAM → `esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi`.
    - Build and flash: `cd firmware/bench/dock_hello && arduino-cli compile -b <fqbn> --build-path <a folder outside the repo> . && arduino-cli upload -b <fqbn> -p <port> --input-dir <that folder> .`
    - Read serial at 115200 baud. Set the baud rate on the same open port that is read (`( exec < $PORT; stty 115200 raw -echo clocal; cat )`); a separate `stty -f` call doesn't stick on macOS.
    - **Before M5:** solder header pins onto the second ESP32-S3 board (X7). It arrived without pins.
  6. **Display test (when the jumpers arrive, about 2026-11-28).** Follow [`firmware/bench/dock_display/README.md`](firmware/bench/dock_display/README.md):
     - First the multimeter check there (touch pins must sit at about 3.3 V, not 5 V, with only power connected).
     - Then wire the 12 wires, flash `dock_display`, and go through its pass table. Nico judges the picture by eye; serial reports touch.
     - Four things are unconfirmed until it runs: color inversion, which way up the picture is, touch direction, backlight polarity. Each has a one-line setting at the top of the sketch.
  7. **Real screens on the display (after step 6 passes).** Follow [`firmware/bench/dock_ui/README.md`](firmware/bench/dock_ui/README.md): copy the working settings over, flash `dock_ui`, and compare the demo screens with `firmware/sim/snapshots/`.
- **M3 look-over (about 5 minutes).**
  1. Terminal A: `cd ~/projects/agent-controller/software/companion-app && source .venv/bin/activate && python -m companion`
  2. Terminal B (same folder and venv): `python ../../tools/sim_bridge.py`. A window opens. Click it.
  3. With two Claude Code sessions running, try: ↑ ↓ (select; the window comes forward after a pause), → (detail), ↑ ↓ (scroll; it should stop at the end), ← (back), and an approval with `s` / `c`.
  4. Say what looks wrong or unlike the reference: sizes, colors, what each row shows.
  - If `make` is needed again: `cd ~/projects/agent-controller/firmware/sim && make`.
- **M1b check on the Mac Mini (about 5 minutes).** **Done 2026-11-26, all passed** (§8); the steps stay here for re-runs. No hook reinstall is needed.
  1. Three windows as in the Mac Mini test below: A `python -m companion`, B `python ../../tools/fake_device.py`, and two or more Claude Code sessions in other tabs.
  2. In B, press ↓ and wait. **After about half a second that session's tab should come to the front.** Flick ↓ ↓ quickly: only the last one should come forward.
  3. Press → to open the detail page, ← to go back. After a finished turn the page should say "Worked for …".
  4. Ask a session to run something that needs permission. In B, **`s` approves** (Enter does nothing now), `c` rejects, ↓ then `s` approves for the session.
  5. If windows jumping forward gets in the way, put `focus_follows_selection = false` in `~/.agent-controller/config.toml`.
- **When parts arrive,** say which ones. M4 (dock on the breadboard) starts once the display and the dock board are both in hand.
- **Repo is public** (checked 2026-11-18), so the website can link to it and load its images.
- **Mac Mini test (M1), about 15 minutes.** **Done 2026-11-11** (results in §1); the steps stay here for re-runs. Steps 3 and 8 (`install-hooks` / `uninstall-hooks`) must be run by Nico — auto mode blocks Claude from editing its own settings. Shortcut: open Claude Code in the repo on the Mac Mini and say "follow HANDOFF.md §6 Mac Mini test with me". It can run steps 1–3 itself.
  1. **Get the code** (after merging the PR):
     - If the repo isn't on the Mac yet: `gh repo clone nicorudu/projects ~/projects` (run `gh auth login` first if needed).
     - Otherwise: `cd ~/projects && git checkout main && git pull`.
  2. **Set up:**
     - `cd ~/projects/agent-controller/software/companion-app`
     - `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
     - `python -m pytest -q` → expect all tests to pass (54 after the hook fixes).
     - Python must be 3.11+; if not, `brew install python@3.12`.
  3. **Install the hooks:** `python -m companion install-hooks` (it prints where the backup went), then `python -m companion doctor`.
  4. **Three terminal windows:**
     - A: `python -m companion`
     - B: `python ../../tools/fake_device.py`
     - C: start `claude` in any project folder.
  5. In C, ask Claude to run something that needs permission, e.g. "run `ls -la ~` with Bash". **B shows the Approval screen.** Press `s` (Send) to approve and check that C continues. Then try: `c` (reject), ↓ + `s` (approve for session), ↑ + `s` (ask in terminal). (Before M1b this was Enter; the stick click is gone.)
  6. On B's Home screen, select the session and press `s`. **C's terminal tab should come to the front.** macOS may ask once to let Terminal/Python control Terminal or iTerm; allow it.
  7. Quit A (Ctrl-C) and ask Claude in C to run another command. **Report back:** does Claude Code show any "hook error" lines, and does its normal permission prompt still appear?
  8. Report anything that looked wrong. `python -m companion uninstall-hooks` removes everything if needed.
- **Recheck after hook fixes (about 5 minutes; after merging PR #5).**
  1. `cd ~/projects && git pull`, then `cd agent-controller/software/companion-app && source .venv/bin/activate && python -m pytest -q`. Expect 54 passed.
  2. `python -m companion install-hooks`, then `python -m companion doctor`. Expect 10 hooks.
  3. **Restart** the Claude Code session in window C, then start A (`python -m companion`) and B (fake device). C must be in `manual mode` (Shift+Tab).
  4. **Answer in C:** ask C to `touch ~/agent-controller-test-9.txt`, then answer in **C's** menu. B should drop the question within a second and show "Answered in the terminal".
  5. **Approve for session from B** (↓ then `s`; Enter before M1b) on `touch ~/agent-controller-test-10.txt`. C's bottom line must still say `manual mode on`.
  6. **App off:** Ctrl-C in A, then ask C to `touch ~/agent-controller-test-11.txt`. There should be **no** "hook error" lines, and C's normal menu appears.

## 7. Open questions
The full list is in blueprint §13. The main ones:
- Which link becomes the default (decided by the M6 test).
- Where the usage header's numbers come from.
- Whether docked sensing and 1 A charging through the dock behave on the breadboard.
- Whether the key plates need the rear hinge, and whether the controller ends up 22 or 24 mm tall.
- What the reference's green button and four contacts really do (check their source code when it's published).
- Four tight spots from the concept model still wait for measurements (blueprint §4.7). The display one is decided: a 13 mm lid, pins bent flat.
- How to get Cursor's "waiting for approval" status.

## 8. Step log (newest first)
- 2026-11-26 — M3 built (Claude Code on the Mac Mini, branch `agent-controller-m3-screens`):
  - Nico chose arduino-cli + Makefile over PlatformIO, and approved installing LVGL 9.6.0, ArduinoJson 7.4.3 (arduino-cli libraries) and SDL2 (Homebrew, as `sdl2-compat`).
  - `firmware/lib/AgentUI`: the screens, with no hardware code. It keeps the last view as JSON and updates objects in place.
  - `firmware/sim`: SDL window, keyboard to protocol inputs, heartbeat, and a headless mode that writes a picture of every screen. `tools/sim_bridge.py` connects it to the app; `tools/sim_fixtures.py` makes the fixtures from the app's own view builder.
  - Checked: 12 snapshots look right (in `firmware/sim/snapshots/`); the window connected to the app on a spare port, stayed connected past the 2 s heartbeat limit, and reported its scroll limit, which the app then enforced. **Not checked: the keyboard in the window** (needs a person).
  - `firmware/bench/dock_ui`: AgentUI with an ST7796S driver; compiles for the dock board. Not flashed.
  - App: `layout` message added; detail scrolling stops at the device's limit. 67 tests.
  - LVGL 9.6 notes: public headers moved to `include/`; `lv_obj_add_flag` is deprecated in favor of `lv_obj_set_hidden` / `lv_obj_set_scrollable`; `LV_COLOR_DEPTH` is replaced by `LV_COLOR_FORMAT_DEFAULT`. LVGL picks up `lv_conf.h` from the AgentUI library by name.
- 2026-11-26 — M1b check on the Mac Mini with real Claude Code sessions (Nico, with Claude Code walking through it). **All passed:**
  - Two sessions appeared and went WORKING → DONE.
  - Focus follows selection: the right Terminal tab came forward each time; with two quick flicks only the last session came forward.
  - Detail page: → opened it, with the "Worked for …" line and the reply; ←, `c` and `g` each went back; Enter did nothing.
  - Approvals: Enter, ← and → did nothing; `s` approved; `c` rejected; ↓ then `s` approved for the session and C stayed on `manual mode on`.
  - A new session showed READY first, then WORKING and DONE.
  - Not tested: IDLE after 10 minutes (covered by a unit test only), and the `focus_follows_selection = false` setting.
  - Nico's choice: focus-follow stays on.
  - Test files `~/agent-controller-test-20.txt` and `-22.txt` can be deleted.
- 2026-11-26 — M1b done in code (Claude Code on the Mac Mini, branch `agent-controller-m1b`):
  - `core/intents.py` rewritten to blueprint §7.1; a test checks every screen and input against the table.
  - Protocol input `click` removed, `green` added. Filters removed from Home.
  - Focus follows selection with a 0.6 s pause (debounced; quiet if the window can't be found). Send focuses at once.
  - Selection is stored as a session id, so the highlight follows its session.
  - `Status.READY` added; new sessions start READY. DONE and READY sessions turn IDLE after `idle_after_s` (600 s).
  - Turn timer on each session (`turn_started`, `worked_s`) for the detail page's "Worked for …" line. Detail text limit raised from 400 to 2,000 characters.
  - Fake device: new key map, status words in capitals, detail page with the time line and a scrolling text window.
  - Tests: 66 pass (was 54), three runs in a row. Focus-follow is off in the test config so tests can't move real windows; its tests use a fake platform.
  - Not done here: Voice review's scroll and destination controls (M2), and the detail page's scroll limit on the real screen (M3 decides the line length).
- 2026-11-26 — Display test written, not flashed (branch `agent-controller-m4-display-test`). PR #18 merged first.
  - `firmware/bench/dock_display/`: ST7796S + FT6336U test with no libraries beyond the ESP32 core. It compiles for the dock board (357 kB). Steps: I2C scan and touch chip ID, backlight fade, red/green/blue fills with timing, a test card, a four-corner tap test, free drawing.
  - Pins are blueprint §5.1. **One addition: touch reset (CTP_RST) on GPIO5**, taken from the free list; §5.1 is updated.
  - Module facts from the LCDWIKI MSP4031 page: 14 pins; VCC 5 V recommended; SDO(MISO) and SD_CS left unconnected. The page gives no voltage for the touch pins, so the README has a multimeter check before the first full hookup.
  - Waiting on the jumper wires (about 2026-11-28).
- 2026-11-26 — M4 bench start done (Claude Code on the Mac Mini, §6 steps 1–5):
  - The dock board (D1) is on `/dev/cu.usbmodem5C850305191`, through its UART/COM port (WCH CH343 bridge, USB ID `1a86:55d3`).
  - Installed with Nico's OK: `arduino-cli` 1.6.0 (Homebrew) and the Espressif ESP32 core 4.0.0.
  - Flashed `firmware/bench/dock_hello/` with Nico's settings (Flash Size = 16 MB, PSRAM = OPI PSRAM). **Pass:** ESP32-S3 rev 2, 2 cores, 240 MHz; flash 16,777,216 bytes (16 MB); PSRAM 8,388,608 bytes (8 MB), found; a 4 MB PSRAM write/read check passed. MAC `7c:4f:ad:bc:aa:6c`.
  - Flash size double-checked on the chip itself with `esptool flash-id`: 16 MB detected (manufacturer `c8`, device `4018`, quad SPI, 3.3 V). The sketch's own flash figure can just repeat the build setting.
  - The board still runs the hello sketch; it prints the report every 3 s and touches no GPIO.
  - **Pins (from Nico):** the dock board (D1) arrived with its pins soldered. The second ESP32-S3 board (X7) arrived **without** pins, so its headers need soldering before M5.
  - Next: the display (blueprint §11).
- 2026-11-26 — Nico sent a photo: most parts have arrived (soldering station, multimeter, heat gun, wire, M2 insert kit, heat-shrink, boards and modules in bags). PR #12 merged. Nico: everything ordered is here except a second XIAO (a spare he ordered; still on the way). BOM statuses set to arrived. The five items from the exact-parts list (C9 resistors, C10 tactile buttons, C11 JST-PH plugs, C12 capacitors, T8 USB-C meter) are ordered and also still on the way; they are only needed for the controller (M5). The display and dock board are in hand, so M4 (dock on the breadboard) can start; first step is plugging the dock board into the Mac Mini.
- 2026-11-19 — Nico asked for exact parts, not generic specs. The shopping list and BOM now name one exact product, quantity and must-match check per line (C9 Geekstory 73-value resistor kit, C10 Hilitchi 6 × 6 mm tactile kit, C11 10-pair JST-PH 2.0 pigtails, C12 500-pc ceramic capacitor kit, T8 Plugable USBC-VAMETER3, plus exact picks for the buy-only-if-needed items). Subtotal is about $70, up from $42, because a data-passing USB-C meter costs $30. Correction: foam tape (S8) is 1.6 mm thick and does not go under the battery; the guard sheet holds the battery. Thumbstick: ordered at the listed quantity (2).
- 2026-11-19 — Nico confirmed the thumbstick and breadboards with jumpers are ordered, and pointed out his second ESP32-S3 board. Decision: one XIAO is enough; the spare board (X7) stands in for the controller on the breadboard. BOM, shopping list, blueprint §3 and §11 updated.
- 2026-11-19 — Parts check against Nico's order screenshots (AliExpress + Amazon):
  - BOM statuses updated; rows marked "Order seen 2026-11-19" are confirmed ordered.
  - Found: only one XIAO was ordered (two are needed); the thumbsticks, resistor kit and breadboards were never ordered; the header strip is no longer needed.
  - New list: `hardware/bom/shopping-list-2026-11-19.md`. PR #10 (concept models) was merged by Nico.
  - Still open: the screen angle for his standing desk (waiting on two measurements) and folding lid vs fixed tilt.
- 2026-11-18 — Fixed-tilt option (rev 3b) mocked up at Nico's request: model, seven renders, overlap check passes, comparison doc `docs/option-fixed-tilt.md`. Not chosen yet.
- 2026-11-18 — Nico chose the thicker lid: 13 mm, display pins bent flat. Model, renders, layout drawing, blueprint §4.1/§4.3/§4.7 and plan updated. Closed size is now about 124 × 112 × 35 mm.
- 2026-11-18 — Rev 3 concept model:
  - `hardware/cad/rev3-pivot/concept.py` builds the device with every part placed, runs an overlap check (passes) and renders eight views.
  - Renders in `hardware/renders/2026-11-18-rev3-concept/`, web copies in `media/web/rev3-02…08`.
  - Blueprint §4.7 added: where each part goes and five tight spots. `showcase.json` hero and timeline updated.
  - Rerun with `xvfb-run -a python3 concept.py` (needs cadquery, trimesh, vtk, manifold3d, Pillow).
- 2026-11-18 — PR #9 merged to `main` at Nico's request (PR #7 closed with it). Started branch `agent-controller-m1b`.
- 2026-11-18 — Shopping list and second parts audit:
  - Wrote `hardware/bom/shopping-list-2026-11-18.md`.
  - BOM: added C11, C12, T8–T11; S6 moved to "to order"; C10 became an assortment.
  - Blueprint: a 0.1 µF capacitor on D2, the battery on a JST-PH pigtail, breadboard tips.
  - Checked nicorudu.com: the project isn't listed there yet. Nico's website chat handles it.
- 2026-11-18 — Opened PR #9 (rev 3 docs; includes PR #7).
- 2026-11-18 — Rev 3:
  - Re-checked every image dropped into the chat (92 files) and re-researched SlashVibe (site, Kickstarter, four demo videos, press).
  - Rewrote the reference notes with a corrections table.
  - Wrote the complete plan (`docs/plan.md`) and blueprint rev 3.
  - Updated the BOM (C10, S6–S9, T6–T7), the architecture's controls table and the decision log.
  - Added the layout drawing and its script (`hardware/cad/rev3-pivot/layout.py`).
  - No code changes.
- 2026-11-12 — M2 planning:
  - Decided Wispr Faux is the voice engine, with dock review then Send/Cancel, Mac first.
  - Rule from Nico: don't edit the wispr-faux repo; use a copy in this project.
  - Saved the link spec draft. M2 tabled for now.
- 2026-11-11 — Mac Mini recheck after PR #5 (all passed):
  - After `git checkout main && git pull` (the Mac had been left on the test branch): 54 tests pass; `install-hooks` installed 10 hooks.
  - Answer-in-terminal cleared B (`pr-1 -> None`, "Answered in the terminal").
  - Approve for session kept `manual mode on`.
  - App off: the normal menu, no hook errors.
- 2026-11-11 — Opened PR #5 (hook fixes).
- 2026-11-11 — Hook fixes (cloud session, branch `agent-controller-hook-fixes`, built on PR #4):
  - All hooks are now silent command hooks (`companion.hooks.report`): async for status, `--wait` for `PermissionRequest`. `PostToolUseFailure` added (10 hooks).
  - Stale questions clear when the session moves on.
  - Approve-for-session only applies `addRules` / `addDirectories`.
  - Out-of-order async events are ignored via `_ts`.
  - 54 tests.
  - Live in the cloud with real Claude Code 2.1.322: approve from the fake device works; app off gives 0 hook errors (every hook exit 0, empty stderr).
- 2026-11-11 — Opened PR #4 (Mac Mini test results + test-race fix) to `main`.
- 2026-11-11 — Mac Mini test (§6) done:
  - Setup: Python 3.14.7. `test_approve` failed on every run on the M4 (Python 3.14 and 3.12 alike): the device's `view` and `led` are separate frames, and the test checked the LED as soon as the Approval view arrived. Fixed the test to wait for both. 45/45 pass, 5 runs in a row.
  - Nico ran `install-hooks` (9 hooks; auto mode blocks Claude from editing its own settings) and steps 4–8.
  - Works: status + LED, Approve, Reject, Ask in terminal, Send-key focus (no macOS prompt), curl to the hook server.
  - Three issues found, assigned to the cloud session: Approve for session applies a `setMode` suggestion; terminal menu and hook race (stale Approval screen on B); `ECONNREFUSED` hook errors with the app off. Details in §1.
- 2026-11-11 — Opened PR #3 (M0 + M1) to `main`.
- 2026-11-11 — M1 done:
  - Hook server, Claude Code plug-in (status + 4-option approvals, timeout and hang-up fallbacks), `install-hooks` / `uninstall-hooks` / `doctor`, SessionStart report script, macOS focus.
  - `main.py` ported to `managed.py` and removed.
  - 45 tests. Verified live against real Claude Code 2.1.322.
  - Docs updated: architecture §3/§6/§8, decisions, build log, README.
- 2026-11-11 — M0 done: companion package, protocol v1 + COBS framing, WebSocket transport, state/intents/view builder, fake device, 28 tests. Added `agent-controller/.gitignore`.
- 2026-11-11 — Created this handoff file. Started M0 on branch `agent-controller-m0-m1`.
- 2026-11-11 — PR #2 merged: software architecture.
- 2026-11-11 — PR #1 merged: repo organized as a physical-product project, rev 2 blueprint, renders, BOM.
