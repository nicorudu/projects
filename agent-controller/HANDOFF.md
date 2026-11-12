# Handoff — AI Agent Controller

**Read this first when picking the project back up** (new chat, after a context reset, or switching to the Mac Mini). It holds the current state, the next step, and the rules. It is updated and pushed after every step.

Last updated: 2026-11-11 · by Claude (cloud session)

---

## 1. Where we are right now
- **Done:** M0 and M1, merged to `main` (PR #3). 45 tests pass, on the Mac Mini too (Python 3.14.7, after a test-race fix on branch `agent-controller-mac-mini-test`).
  - M1 was **verified live** twice: real Claude Code 2.1.322 in the cloud workspace (hook → fake device Approve → the command ran), then the full §6 test on the Mac Mini.
- **Mac Mini test — done 2026-11-11.** Hooks are installed on the Mac Mini (venv at `software/companion-app/.venv`). Note: Claude Code's auto mode won't let Claude run `install-hooks` / `uninstall-hooks` (it edits Claude's own `~/.claude/settings.json`), so Nico runs those.
  - **Works:**
    - Status on the fake device (working / waiting / done, LED).
    - Approve: C's own menu closed by itself; C showed "Allowed by PermissionRequest hook".
    - Reject (`c`): "Denied by PermissionRequest hook"; Claude didn't retry.
    - Ask in terminal (↑ Enter): B said "Answer in the terminal", C's menu answered normally, the row went to done.
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

| # | What | Hardware? | State |
|---|---|---|---|
| M0 | Package restructure, protocol v1, WebSocket transport, state/intents/view, fake device | No | **done** (2026-11-11) |
| M1 | Claude Code hooks: live status + approvals from the fake device; install/uninstall hooks | No (Mac Mini to test live) | **done** (2026-11-11), Mac Mini tested and fixes rechecked |
| M2 | Voice: Wispr Faux (a copy in this project) as the engine, dock review + Send/Cancel | No (Mac Mini) | planned, tabled (see §1) |
| M3 | LVGL UI in the desktop simulator (PlatformIO `sim` env) | No | planned |
| M4 | Dock firmware: display, touch, USB + Wi-Fi transports | Yes | waits for parts |
| M5 | Controller firmware: keys, stick, mics, battery, ESP-NOW | Yes | waits for parts |
| M6 | USB vs Wi-Fi latency shoot-out, print CAD from caliper measurements | Yes | waits for parts |

## 3. Standing rules (from Nico)
1. **Document everything in GitHub after every step**, and update this handoff, so nothing is lost when the chat compacts.
2. **Audit shopping lists rigorously.** Every part change goes into `hardware/bom/BOM.csv` with a status. Past misses cost real shipping time.
3. **Website (nicorudu.com):** don't edit it. Write the exact fixes for Nico to hand to his website Claude assistant.
4. **v0 should be as close to v1 as possible**, and the printed shell should look as accurate to the reference (SlashVibe) as possible.
5. **Git:** branch first, never commit to `main`. Commit author `nicorudu <nicorudu@users.noreply.github.com>`. Never put Nico's personal email in commits or external requests.
6. **Secrets** (Groq, Anthropic keys) go in the OS keychain via `keyring`, never in the repo.
7. Nico uses an **M4 Mac Mini** (main; Claude Code runs better there) and an **HP OmniBook X Flip (Windows)**. Code must run on both.

## 4. Design in one paragraph
Desk dock (ESP32-S3 N16R8 DevKitC, 4" ST7796 touch screen on a fold-flat hinge, MAX98357A + 40 mm 4 Ω 2 W speaker, WS2812B, USB-C to the Mac on the back) plus a detachable controller bar (XIAO ESP32S3, 3 Choc keys = Cancel / Voice / Send, Adafruit #5628 Joy-Con stick with a flat printed cap, 2× INMP441 mics, 1000 mAh LiPo, TP4056, slide switch, LED). The controller sits on magnets and charges through a 2-pin magnetic pogo connector. Two data paths, built and timed side by side: **A** Wi-Fi WebSocket, **B** dock USB CDC with the controller relayed over ESP-NOW. A Python companion app on the computer does all the logic; the dock only draws the screens it's sent.

Full detail: [blueprint](docs/agent-controller-v0-blueprint.md) (parts, pin maps, power, protocol, voice, plug-ins, tests) · [architecture](docs/architecture.md) (code layout, state, screens/keys, hooks, milestones) · [decisions](docs/decisions.md) · [build log](BUILDLOG.md).

## 5. Key technical facts (so they don't need re-researching)
- **Pins.** Dock: never use GPIO35–37 (octal PSRAM). Avoid strapping pins 0/3/45/46. Controller: all 11 XIAO pins are used; analog on ADC1 only. Full maps are in blueprint §4.
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
- **Order:** C1 XIAO ESP32S3 ×2, C2 Adafruit #5628 ×2, D7 magnets, S4 header strip, C9 resistor kit (needs 100 kΩ). Confirm C7 TP4056 was ordered.
- **Arrivals:** AliExpress 5–10 days from ~2026-11-09; speaker ETA ~2026-11-20. On arrival, measure the stick, display and pogo connector with calipers so the print CAD can be finalized.
- **Repo is private.** Make it public when you want the website to link to it and load its images.
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
  5. In C, ask Claude to run something that needs permission, e.g. "run `ls -la ~` with Bash". **B shows the Approval screen.** Press Enter to approve and check that C continues. Then try: `c` (reject), ↓ + Enter (approve for session), ↑ + Enter (ask in terminal).
  6. On B's Home screen, select the session and press `s`. **C's terminal tab should come to the front.** macOS may ask once to let Terminal/Python control Terminal or iTerm; allow it.
  7. Quit A (Ctrl-C) and ask Claude in C to run another command. **Report back:** does Claude Code show any "hook error" lines, and does its normal permission prompt still appear?
  8. Report anything that looked wrong. `python -m companion uninstall-hooks` removes everything if needed.
- **Recheck after hook fixes (about 5 minutes; after merging PR #5).**
  1. `cd ~/projects && git pull`, then `cd agent-controller/software/companion-app && source .venv/bin/activate && python -m pytest -q`. Expect 54 passed.
  2. `python -m companion install-hooks`, then `python -m companion doctor`. Expect 10 hooks.
  3. **Restart** the Claude Code session in window C, then start A (`python -m companion`) and B (fake device). C must be in `manual mode` (Shift+Tab).
  4. **Answer in C:** ask C to `touch ~/agent-controller-test-9.txt`, then answer in **C's** menu. B should drop the question within a second and show "Answered in the terminal".
  5. **Approve for session from B** (↓ Enter) on `touch ~/agent-controller-test-10.txt`. C's bottom line must still say `manual mode on`.
  6. **App off:** Ctrl-C in A, then ask C to `touch ~/agent-controller-test-11.txt`. There should be **no** "hook error" lines, and C's normal menu appears.

## 7. Open questions
- Which transport becomes the default (decided by the M6 shoot-out).
- How to get Cursor's "waiting for approval" status (which Cursor hooks fire).
- Cloud agent APIs (ChatGPT, Grok, etc.) for status, beyond focus + paste.
- Controller battery life on Wi-Fi vs ESP-NOW.

## 8. Step log (newest first)
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
