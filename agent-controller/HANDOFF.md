# Handoff — AI Agent Controller

**Read this first when picking the project back up** (new chat, after a context reset, or switching to the Mac Mini). It holds the current state, the next step, and the rules. It is updated and pushed after every step.

Last updated: 2026-11-11 · by Claude (cloud session)

---

## 1. Where we are right now
- **Done:** M0 and M1, pushed on branch `agent-controller-m0-m1`, with a PR open to `main` (number in the step log). 45 tests pass.
  - M1 was **verified live**: real Claude Code 2.1.322 in the cloud workspace → our `PermissionRequest` hook → fake device Approve → the command ran.
- **Waiting on Nico:**
  1. Merge the PR.
  2. Do the Mac Mini test in §6. The steps that need a real Mac are terminal-tab focus, macOS permission prompts, and how Claude Code behaves when the app is off.
- **Next step (M2): voice on the Mac mic.**
  - Speech-to-text interface: `stt.transcribe(audio, vocab)`, using mlx-whisper locally with Groq as the fallback.
  - Claude cleanup with modes prompt / message / email.
  - Personal dictionary at `~/.agent-controller/dictionary.yaml`; API keys in the keychain.
  - Delivery: paste into the focused terminal tab, or start a managed session.
  - The Mac mic stands in for the controller mics until hardware.
- **M1 design notes (from the hooks docs, rechecked 2026-11-11):**
  - `SessionStart` accepts only command hooks. We use an async command hook that runs `python -m companion.hooks.report`, which posts the event plus the terminal app and TTY.
  - All other events are `http` hooks to `/hooks/claude`. Status hooks get a 2 s timeout. `PermissionRequest` gets 600 s; the app itself answers within `approval_timeout_s` (120 s), or with no decision.
  - While a `PermissionRequest` hook is open, the terminal waits. So the Approval screen has 4 options: Approve / Approve for session / Reject / Ask in terminal (= no decision → normal prompt).
  - "Approve for session" = `allow` + `updatedPermissions` = the request's `permission_suggestions` with `destination` changed to `"session"`.
  - Hook server checks: loopback only, `Host` must be localhost/127.0.0.1, and the body must be JSON (blocks browser cross-site posts).
  - To check on the Mac Mini: whether a refused connection (app not running) prints a "hook error" line in Claude Code. If it does, the fix is to run `uninstall-hooks` when not using the device, or switch status hooks to async command hooks.
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
| M1 | Claude Code HTTP hooks: live status + approvals from the fake device; install/uninstall hooks | No (Mac Mini to test live) | **done** (2026-11-11), Mac Mini check pending |
| M2 | Voice on the Mac mic: Whisper (mlx / Groq fallback) + Claude cleanup + dictionary | No (Mac Mini) | next |
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
  - The `http` hook type POSTs the event JSON to a URL. The default timeout is 600 s, and a failure is non-blocking.
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
- **Mac Mini test (M1), about 15 minutes.** Shortcut: open Claude Code in the repo on the Mac Mini and say "follow HANDOFF.md §6 Mac Mini test with me". It can run steps 1–3 itself.
  1. **Get the code** (after merging the PR):
     - If the repo isn't on the Mac yet: `gh repo clone nicorudu/projects ~/projects` (run `gh auth login` first if needed).
     - Otherwise: `cd ~/projects && git checkout main && git pull`.
  2. **Set up:**
     - `cd ~/projects/agent-controller/software/companion-app`
     - `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
     - `python -m pytest -q` → expect 45 passed.
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

## 7. Open questions
- Which transport becomes the default (decided by the M6 shoot-out).
- How to get Cursor's "waiting for approval" status (which Cursor hooks fire).
- Cloud agent APIs (ChatGPT, Grok, etc.) for status, beyond focus + paste.
- Controller battery life on Wi-Fi vs ESP-NOW.

## 8. Step log (newest first)
- 2026-11-11 — M1 done:
  - Hook server, Claude Code plug-in (status + 4-option approvals, timeout and hang-up fallbacks), `install-hooks` / `uninstall-hooks` / `doctor`, SessionStart report script, macOS focus.
  - `main.py` ported to `managed.py` and removed.
  - 45 tests. Verified live against real Claude Code 2.1.322.
  - Docs updated: architecture §3/§6/§8, decisions, build log, README.
- 2026-11-11 — M0 done: companion package, protocol v1 + COBS framing, WebSocket transport, state/intents/view builder, fake device, 28 tests. Added `agent-controller/.gitignore`.
- 2026-11-11 — Created this handoff file. Started M0 on branch `agent-controller-m0-m1`.
- 2026-11-11 — PR #2 merged: software architecture.
- 2026-11-11 — PR #1 merged: repo organized as a physical-product project, rev 2 blueprint, renders, BOM.
