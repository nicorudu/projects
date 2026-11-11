# SlashVibe — reference for the agent controller build

Researched Nov 11, 2026, from slashvibe.ai, the live Kickstarter (campaign, specs, FAQ, update #1, comments), the privacy/terms/shipping pages, Gadget Flow's launch article and launch-tracking pages. Facts are quoted from those sources. Anything read off a photo or drawing rather than stated in text is marked **(from images)**; anything I inferred is marked **(inferred)**.

---

## 1. What it is

A desk accessory for running AI agents: an always-on display unit that sits beside your computer, plus a detachable handheld controller with keys, a joystick and microphones. Tagline: "Your AI workspace, right by your side." Three jobs: agent monitoring/approvals, voice-driven to-dos, and meeting assistance. Voice dictation works in any app, not just agents.

The display is a thin client. Per the FAQ, custom software "runs on your computer, with its interface streamed to SlashVibe." The computer app (SlashVibe+) does the work; the hardware shows UI and sends input. Same split as our companion-app design.

---

## 2. Hardware

### Overall
| Spec | Value |
|---|---|
| Size, assembled | 4.13 × 3.52 × 0.82 in (≈ 105 × 89 × 21 mm) |
| Weight, assembled | 9.70 oz (≈ 275 g) |
| Colors | Black or Silver (chosen in post-campaign survey) |
| Computer support | macOS and Windows |
| In the box | SlashVibe V1 (display unit + controller), USB-C data cable, user manual |

### Display unit
| Spec | Value |
|---|---|
| Display | 3.96-inch LCD (resolution not published) |
| Speaker | Built-in 2 W |
| Connection | USB-C for power **and** data to the computer |
| Material | Sandblasted, anodized aluminum housing and base |
| Feet | Silicone |
| Form **(from images)** | Screen on a hinge at the back of a low base; folds flat to a closed "compact" shape. Base top has a ribbed/slotted texture. |

The FAQ says the wire is deliberate: it "helps keep voice input latency low, provides continuous power, and keeps the connection reliable."

### Handheld controller
| Spec | Value |
|---|---|
| Action keys | Kailh ultra-low-profile mechanical switches, travel 1.8 ± 0.3 mm, tactile force 52 ± 15 gf |
| Keycaps | Sandblasted anodized aluminum |
| Joystick | Two-axis, 2 mm travel per side, force 85 ± 30 g; soft-touch ABS+PC cap |
| Mics | Dual MEMS |
| Link to display | 2.4 GHz wireless |
| Battery | 500 mAh rechargeable, 20 hours |
| Charging | "The controller charges magnetically when attached to the display unit. When the display unit is connected to a computer via USB-C, its contact pins charge the controller." |
| Housing | ABS+PC with soft-touch upper surfaces |

**Layout (from images):**
- One rigid straight bar: three keys in a row, then a square joystick block at one end. The spec drawing shows no pivot.
- The joystick cap is a flat, wide disc sitting in a round recess, with tick marks at the four directions. The cap's center is perforated.
- A small status LED (green in renders) sits next to the joystick.
- Two perforated mic grilles are on the end face of the joystick block, so you speak into the end of the bar.
- Docked, the bar lies along the front edge of the display base: keys on the left, joystick on the right.
- Handheld, it's held upright like a remote, joystick at the top.

**"Rotate it":** the Desktop mode copy says "Turn the controller so the joystick lands under your thumb." In the desktop photo the whole bar is turned on the desk. Nothing in the text or the spec drawing shows a joystick block that swivels separately.

**Key functions (inferred):** the keycap icons read as cancel (⊘), voice (wave lines) and send (arrow). The copy describes a dedicated voice key, a Send press and a Cancel press.

---

## 3. Software and interaction

### Agent view
- Every agent session is a row with a status: **WORKING, WAITING, DONE, ERROR** (from images; color-coded blue/yellow/green/red) and a pixel-art agent icon.
- A header strip shows API spend (e.g. "API $92.6") and usage meters ("5h 38% 7d 4%") **(from images)**. These look like Claude's 5-hour and weekly usage windows **(inferred)**.
- "Flick to select. Flick to open." Selecting a session brings its window to the front on the computer.
- **Approvals on device:** the permission prompt appears on the screen with options like "Reject this permission request / Approve this request and allow changes to project files / Approve all requests for this session" (from images). This mirrors Claude Code's own prompt.
- When an agent stops and waits, the status updates and a short alert sound plays. The sound can be turned off.
- **Work Brief:** a summary of what's done, what's running and what's next across agents.

### Voice
- Press the dedicated key; ready to record in under 100 ms. "It's a dedicated key, so it won't clash with shortcuts in your other apps."
- Built-in dictation: removes filler words, fixes formatting, and adapts tone ("precise for prompts, polished for emails, natural for quick messages").
- A personal dictionary auto-learns project names, libraries and teammates' names.
- With permission, it reads on-screen text (OCR) for context. Only the text is sent; screenshots stay local.
- "Press Send" to deliver, "edit it by voice," "Press Cancel, and nothing gets sent."
- Works anywhere you can type. Languages: English, Spanish, French, German, Portuguese, Chinese, Japanese, Korean "and more."
- Close-talk use: hold the controller near your mouth and whisper.

### To-dos
- Captured by voice. Each to-do can carry one or more AI tasks underneath it, with progress shown.
- Hand off a to-do to an agent session and see its status next to the list item.

### Meetings
- Works with Zoom, Google Meet and Microsoft Teams, plus Google Calendar and Outlook.
- Live notes on the display with scrollback.
- Use the joystick to flick through suggested prompts ("Catch me up", "Break that down", "What should I ask"); answers appear on the device.
- One-tap mute/record. A calendar event can switch to meeting mode and start recording.
- Action items become to-dos and agent tasks afterward.

### Supported agents (FAQ list)
Claude Code CLI and Desktop, Claude Cowork, Codex CLI and Desktop, Copilot CLI, OpenCode v2 CLI, Pi Agent, Oh My Pi, Grok Build CLI, Cursor, Antigravity CLI, Hermes, DSH, Droid, Trae, Kiro, WorkBuddy, MiMo Code, ZCode, Gemini CLI, Qoder, Qwen, Kimi, Kimi Code. An "open integration layer" is in progress.

### Developer SDK
- Write tools in **Node.js or Python**, no firmware work. The SDK covers custom screen layouts, button and joystick events, and voice transcript text.
- Code runs on the computer; its interface is streamed to the device.
- Examples: unsupported agents, API-spend tracker, deadline countdown, do-not-disturb timer, a garden that grows as agents finish tasks, a pixel pet, a mini game.
- Built-in screen names in the website's image files **(inferred from filenames)**: garden, portfolio, arcade, briefing, prs, pet, heatmap, weather, radio, watchlist, fishing, calendar, shipped, dice, news, focus, aquarium, spend, catnap, todo, clocks, habit, sprint, music, muse.

### Privacy model
- Agent sessions and context: processed and stored only on the computer.
- Audio: only while recording, transcribed in the cloud, never stored there.
- Screen text: OCR text only; screenshots never leave the computer.
- Providers can't train on the data. Cloud sync is off unless enabled.
- Cloud model providers are not named.

---

## 4. Business

| Item | Detail |
|---|---|
| Company | Natural Mapping, Inc., dba SlashVibe (Delaware; address 8 The Green, Ste RD, Dover, DE 19901) |
| Founder | Loda (co-founder). Previously co-founded a split/ergonomic keyboard brand. Contact loda@slashvibe.ai |
| Team | 14 people shown on the campaign |
| Manufacturing | Dongguan, China; co-founder manages the supply chain and works with the factory directly; team has shipped hardware to the US, Korea and Japan |
| Timeline | Concept Nov 2025 → design locked Jul 2026 → first review units Sep 2026 → Kickstarter Nov 10, 2026 → shipping Mar 2027 |
| Status | Terms of service: "a working prototype and is not yet in production." FCC certification still to pass (battery + wireless controller). |
| Launch teaser | 1:14 video on X, Oct 14, 2026; ~294K views |
| Campaign | $10,000 goal, funded on day 1. **$65,470 from 284 backers** as of Nov 11 morning. Ends **Thu Dec 10, 2026, 10:54 AM EST**. All-or-nothing. Promoted by Jellop. |

### Pricing
| Item | Price |
|---|---|
| MSRP | $249 |
| Kickstarter "Day 1 Special" | $169 (launch day only), ships worldwide, est. delivery Mar 2027. The Kickstarter graphics say taxes and duties are included. |
| VIP price | $149, unlocked by a $1 reservation before launch |
| Also on their reservation page | $189 (tier not labeled) |
| Add-ons | Carrying case $24, magnetic coil cable $19 |

### Software plans (Kickstarter version)
| | Free | Lite | Pro |
|---|---|---|---|
| Price | $0 | $10/mo or $100/yr | $24/mo or $240/yr |
| AI credits / month (one pool) | 200 | 2,000 | 5,000 |
| Meeting assistant (if all credits spent here) | ~2 hrs | ~20 hrs | ~50 hrs |
| Voice & AI writing | 3,200 words | 32,000 words | Unlimited (fair use; doesn't use credits) |
| Hand off to agent | 50 to try | 1,000 | 2,500 |
| Cloud sync | No | Yes | Yes |

- Agent status, approvals, to-do list and recording controls are free on every plan.
- Every unit includes 1 month of Pro; AI features can also run on your own API key.
- slashvibe.ai's main page still says "$8 and $14 per month." The Kickstarter table is newer and differs.

---

## 5. What this means for our build

**Matches our plan**
- Thin-client architecture: computer app does the work, device shows UI and sends events. Our companion app plus WebSocket setup is the same model.
- Dock + detachable controller, with the controller charged through contact pins when docked. Our magnetic pogo connector does exactly this.
- 3 low-profile Kailh keys, a 2-axis stick, dual MEMS mics on the controller, a 2 W speaker in the display unit.
- A ~4" LCD: theirs 3.96", ours 4.0" ST7796 (320×480).

**Corrections to our design**
1. **No swiveling joystick block.** Their controller is one straight bar (3 keys + joystick end). "Rotate" means turning the whole bar on the desk. We drop the pivot, and with it the wires through a pivot. Magnets stay on the list: they hold the controller onto the dock contacts.
2. **Mics go on the joystick end face**, not under the top grille. Two small grilles on the end you speak into.
3. **Status LED beside the joystick on the controller.** Our second WS2812B goes there.
4. **Dock layout:** screen on a fold-flat hinge at the back of a low base; the controller lies along the base's front edge, keys left and stick right.
5. **Key mapping:** Cancel / Voice / Send instead of approve / back / mic. Approvals happen on screen: flick to the option, press to confirm. That matches their approval UI.
6. **Joystick cap:** flat wide disc in a round recess with four direction ticks. Our printed cap should copy this.

**Where we differ, and the trade-offs**
- **Computer link.** Theirs is USB data, chosen for voice latency and reliability. Ours is Wi-Fi to the companion app. Since our dock is USB-powered anyway, USB serial is an easy upgrade path if Wi-Fi voice latency disappoints.
- **Controller radio and battery.** Theirs is a 2.4 GHz link to the dock, getting 20 h from 500 mAh. Our XIAO talks Wi-Fi straight to the companion app; Wi-Fi draws far more than a low-power 2.4 GHz link. Expect hours rather than 20 h even with our 1000 mAh cell **(inferred)**. Measure it in week 1. If battery life is poor, the fallback is ESP-NOW (low-power ESP32-to-ESP32) from controller to dock, which mirrors their architecture.
- **Size.** Theirs is ≈ 105 × 89 × 21 mm closed. Our display module alone is 108 mm wide, so our dock will be roughly 115–120 mm wide.
- **Keys.** Their "ultra-low-profile" Kailh switches are thinner than our Choc v1. Ours will sit a few mm taller; fine for v0.
- **Joystick travel.** Theirs is 2 mm per side. The Adafruit stick has more travel (exact figure unpublished); measure on arrival.

**Software ideas worth copying in order**
1. Session list with WORKING / WAITING / DONE / ERROR plus an alert sound on WAITING.
2. On-device approval prompt (needs the PTY approval flow we deferred to v1).
3. Push-to-talk → cleaned transcript → Send/Cancel.
4. Usage header (API spend, 5h/7d usage).
5. Work Brief.
6. Later: to-dos, meetings, custom screens.

**Still unknown**
- Display resolution and the exact LCD panel.
- The controller's MCU and radio chip.
- Charging time.
- What the joystick click does, or whether the stick clicks at all.
- How the controller is held on the dock beyond "magnetically."
- Which cloud speech provider they use.

---

## Sources
- slashvibe.ai (home, /earlybird, /vip, /privacy, /terms, /shipping)
- Kickstarter: kickstarter.com/projects/loda/slashvibe (campaign, FAQ, update #1, comments)
- Gadget Flow, "SlashVibe gives your AI tools their own spot on the desk," Nov 10, 2026
- whatships.com/videos/slashvibe and doomers.ai/launches/slashvibe (launch video stats)
