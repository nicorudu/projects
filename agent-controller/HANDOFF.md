# Handoff — AI Agent Controller

**Read this first when picking the project back up** (new chat, after a context reset, or switching to the Mac Mini). It holds the current state, the next step, and the rules. It is updated and pushed after every step.

Last updated: 2026-11-11 · by Claude (cloud session)

---

## 1. Where we are right now
- **Current step:** M0 — restructure the companion app into the `companion/` package (protocol, state store, intents, view builder, WebSocket transport) plus `tools/fake_device.py`.
- **Branch:** `agent-controller-m0-m1` (from `main` at `0fce74a`, after PR #2 merged). No PR yet.
- **Next step after that:** M1. Hook server on `127.0.0.1:8766`, Claude Code plug-in, approvals from the fake device, `install-hooks` / `uninstall-hooks`.
- **When Nico needs to switch to the Mac Mini:** once M1 is pushed. Run `install-hooks`, then approve a real Claude Code edit from the fake device. Exact steps go in §6 when ready.

## 2. Milestones

| # | What | Hardware? | State |
|---|---|---|---|
| M0 | Package restructure, protocol v1, WebSocket transport, state/intents/view, fake device | No | **in progress** |
| M1 | Claude Code HTTP hooks: live status + approvals from the fake device; install/uninstall hooks | No (Mac Mini to test live) | next |
| M2 | Voice on the Mac mic: Whisper (mlx / Groq fallback) + Claude cleanup + dictionary | No (Mac Mini) | planned |
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
- **Mac Mini switch:** not yet. The instructions will appear here when M1 is ready.

## 7. Open questions
- Which transport becomes the default (decided by the M6 shoot-out).
- How to get Cursor's "waiting for approval" status (which Cursor hooks fire).
- Cloud agent APIs (ChatGPT, Grok, etc.) for status, beyond focus + paste.
- Controller battery life on Wi-Fi vs ESP-NOW.

## 8. Step log (newest first)
- 2026-11-11 — Created this handoff file. Started M0 on branch `agent-controller-m0-m1`.
- 2026-11-11 — PR #2 merged: software architecture.
- 2026-11-11 — PR #1 merged: repo organized as a physical-product project, rev 2 blueprint, renders, BOM.
