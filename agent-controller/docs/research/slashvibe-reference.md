# SlashVibe — reference for the agent controller build (rev 2)

Rewritten 2026-11-18. It replaces the 2026-11-11 notes and corrects them.

**How to read it.** Facts stated in SlashVibe's own text are plain. Anything read off a photo, drawing or video is marked **(seen)**. Anything worked out from those is marked **(inferred)**.

**Sources checked on 2026-11-18**
- slashvibe.ai: home page, spec drawing, FAQ.
- Kickstarter: campaign, FAQ (17 answers), updates #1–2, comments.
- SlashVibe's four YouTube videos: the brand film and the agents, to-do and meeting demos.
- The Gadgeteer (Nov 15), Gadget Flow, Freeyork and Gadgetify articles.
- Every photo Nico dropped into the chat, including SlashVibe's own teardown photo (X, Oct 12).

---

## 1. Corrections to the 2026-11-11 notes

| # | What the old notes said | What's true | Evidence |
|---|---|---|---|
| 1 | "The joystick does **not** swivel. Rotate means turning the whole bar." | **The joystick block pivots about 90°.** It swings out so the stick sits under your thumb while your fingers stay on the keys. Nico pointed this out on Nov 9 and was right. | Nico's photo (block swung out while docked); brand film at 0:26 (block angled on a detached controller); site copy "Rotate it. The joystick falls right under your thumb."; teardown (pivot ear on the housing, long flex cable) |
| 2 | Keys in the order Cancel / Voice / Send | **Cancel / Send / Voice**, with Voice next to the joystick | Hero photo, brand film, spec drawing. One early render shows a different order; photos of real units win. |
| 3 | The stick may click | **No click.** The stick has two axes only. | Teardown: the stick module has 3 + 3 pins (two potentiometers). Spec: "Two-axis joystick". |
| 4 | "Status LED beside the joystick" | It's a small **button with a green cap** (it may also light up) | Teardown: a tactile switch and a green pill-shaped cap; close-up render shows a pin-hole in the cap |
| 5 | Charging through "contact pins" (we assumed 2) | **4 contacts** between dock and controller | Teardown: two 4-pin pogo strips; 4 pads on both boards |
| 6 | Keys roughly keyboard-key size | Keys are **large plates**, about 21 × 38 mm each, flush with the base top | Teardown and close-ups, scaled from the 104.9 mm width |
| 7 | Home screen: stick left/right changes a filter | Stick **right opens** a session's detail page, **left goes back**. No filters. | Agents demo video |

---

## 2. Hardware

### Published specs
| Spec | Value |
|---|---|
| Size, assembled | 4.13 × 3.52 × 0.82 in (104.9 × 89.4 × 20.8 mm) |
| Weight | 9.70 oz (275 g) |
| Display | 3.96-inch LCD (resolution not published) |
| Connection | Display unit: USB-C for power **and** data. Controller: 2.4 GHz wireless to the display unit. |
| Keys | Kailh ultra-low-profile mechanical switches; travel 1.8 ± 0.3 mm; tactile force 52 ± 15 gf |
| Joystick | Two-axis; travel 2 mm per side; force 85 ± 30 g |
| Battery | 500 mAh rechargeable; 20 hours |
| Audio | Dual MEMS microphones; built-in 2 W speaker |
| Materials | Sandblasted, anodized aluminium display housing, base and keycaps; ABS+PC controller housing with soft-touch top; soft-touch joystick cap; silicone feet |
| Colors | Black or Silver |
| Computers | macOS and Windows (Linux by the community) |
| In the box | The unit, a USB-C data cable, a manual |

### Shape and layout (seen)
- **Three bodies:** a lid with the screen, a base, and the controller.
- **Lid:** aluminium frame around a bare LCD. It hinges at the back of the base on two corner knuckles and a polished rod, and folds flat into a slab. The wordmark is on the lid.
- **Base:**
  - Its whole top is a ribbed aluminium grille. The spec drawing labels this as the **speaker**.
  - The speaker inside is a small sealed white box with a slot port, not a bare round cone.
  - A row of small vent slots runs along one side.
  - The USB-C cable leaves from the back.
  - The bottom is a flat plate with four corner screws.
- **Controller:**
  - It sits in front of the base and is the same width, with its top flush with the base top.
  - It attaches to the base's front face, where the 4 contacts are.
  - **Key section:** three large aluminium key plates in a row, and the wordmark on the front lip.
  - **Joystick block:** square, at one end.
    - A wide, low disc cap with a dimpled centre sits in a shallow round dish.
    - Four tick marks at up, down, left and right.
    - The green-capped button is at one corner.
    - **Two oval mic grilles are on the end face**, with a tiny hole between them.
- **Pivot:** the block hangs off an ear at the **front corner** of the joint. Swung out, it points toward you and leaves a gap where it was. A long flex cable crosses the joint.
- **Three ways to hold it:**
  - **Docked, in line:** the compact shape.
  - **Handheld, in line:** held upright like a remote, with the joystick and mics at the top near your mouth.
  - **Desktop, block swung out:** docked or detached, fingers on the keys and thumb on the stick.

### Approximate sizes (inferred, scaled from the teardown photo)
| Part | Size |
|---|---|
| Base | 105 × ~49 mm |
| Controller | 105 × ~40 mm |
| Key section | ~64 × 40 mm |
| Joystick block | ~41 × 40 mm |
| Each keycap | ~21 × 38 mm |
| Lid | 105 × ~74 mm |

### Inside (seen in the teardown)
- **Dock:** one main board with a large chip and a USB-C socket, a strip board with two wide display connectors, the box speaker, and a 4-pin pogo strip.
- **Controller key section:** one board with a small processor, a battery socket and a flex socket; a small LiPo pouch; a 4-pin pogo strip; three low-profile switch mechanisms; three clear frames under the keycaps (so the icons can probably light up).
- **Joystick block:** a board with a cut-out for the stick, two mics on its outer edge, and the small button; the black low-profile stick module.
- A small finned metal block. Its purpose is unknown.
- Chip names can't be read in the photo.

---

## 3. How it's used

### Controls (seen in the demo videos, unless marked)
| Control | What it does |
|---|---|
| Stick up / down | Move the selection. Selecting a session brings its window to the front on the computer. |
| Stick right | Open the selected item's detail page |
| Stick left | Back |
| **Voice** key (hold) | Record. Recording is ready in under 100 ms. The demo's on-screen guide highlights the key in green; the real keys have clear frames under them, so they may light up **(inferred)**. |
| **Send** key | Deliver the dictated text. Probably also confirms a choice **(inferred)**. |
| **Cancel** key | "Press Cancel, and nothing gets sent." Probably also rejects or backs out **(inferred)**. |
| Green button | Not documented. Likely power, pairing or switching workspace **(inferred)**. |
| In a meeting | "Tap to record, mute, or end"; flick to open a menu of prompts |

### Screens
- **Agents:**
  - Header strip with API spend and usage, e.g. `API $307.5 · 5h 68% · 7d 9%`. A newer build shows `5H 33% 7D 90% | USAGE 50.5M`.
  - One row per session: a colored dot, a status word, and the task title.
  - The selected row has an outline in its status color.
  - Status words seen: WORKING, WAITING, DONE, ERROR, plus IDLE and READY in the newest demo, and NEEDS YOU in one image.
- **Session detail:** title bar with the status dot, a line like "Worked for 6m 24s", then the agent's last message with a scrollbar.
- **Approval:** the agent's request with options, like Claude Code's own prompt (reject / approve / approve all for this session).
- **Voice:** a glowing waveform along the top edge while recording and a live transcript bubble at the bottom.
- **To-dos (`/todo`):**
  - "Hold to say it" captures a to-do by voice.
  - Each to-do can have AI tasks under it.
  - Flick right to see progress.
- **Meetings (`/meeting`):**
  - Live notes with timestamps.
  - A flick opens the prompt menu: Catch me up / Break that down / Make me sound smart / What should I ask? / More Slashes.
  - A summary and to-dos at the end.
  - Works with Zoom, Google Meet and Teams; the official plugin comes after launch.
- **Alert:** a short sound when an agent starts waiting. It can be turned off.

### Voice
- Its own dictation software: removes filler words, fixes formatting, uses your own terms, and adjusts tone (precise for prompts, polished for emails, natural for messages).
- A personal dictionary that picks up project names, libraries and teammates' names.
- "Speak quietly. Send when you're ready." You can edit by voice. Cancel sends nothing.
- Works anywhere you can type.
- Cloud speech-to-text by default.
- **Local models are supported.** The founder named Qwen3-ASR or Whisper for transcription and Qwen3.5-2B for cleanup.
- Languages: English, Spanish, French, German, Portuguese, Chinese, Japanese, Korean and more.

### Software
- **SlashVibe+** desktop app for macOS and Windows.
- "Your custom software runs on your computer, with its interface streamed to SlashVibe." So the device is a thin client.
- **20+ agents**, including Claude Code (CLI and Desktop), Claude Cowork, the ChatGPT app, Codex, Copilot CLI, Cursor, Gemini CLI, OpenCode and Grok Build CLI.
- **SDK** in Node.js and Python: custom screen layouts, button and joystick events, and transcribed voice text.
- **Open source:**
  - The desktop app, device firmware, communication protocol and SDK will be released under **GNU AGPL-3.0**.
  - Update #2 (Nov 18) says "within the next month".
  - Hardware design files are not included.
- **Privacy:** agent sessions stay on the computer; audio is only sent while you record; cloud sync is off by default.

---

## 4. Business
| Item | Detail |
|---|---|
| Company | Natural Mapping, Inc., dba SlashVibe (Dover, Delaware). Made in Dongguan, China. |
| Founder | Loda, who previously co-founded a split-keyboard brand |
| Industrial design | Changliang Liu, Yitian Wu and Shijun Xu of dooo design (per Freeyork) |
| Kickstarter | $146,688 from 652 backers on Nov 18 (goal $10,000). "Project We Love". Ends Dec 10, 2026. |
| Price | Early Bird $189 (8 of 210 left); two for $368; retail $249; the $169 day-one tier is gone |
| Add-ons | Carrying case $24; magnetic coil cable $19 |
| Shipping | First batch expected March 2027. FCC testing still to pass. |
| Software plans | A free plan. Paid plans add cloud voice and sync; pricing "before shipping". You can use third-party or local voice instead. |

---

## 5. Still unknown
- Display resolution and the panel model.
- Which chips are used, and what the 2.4 GHz link is.
- What the four contacts carry (power only, or power and data).
- What the green button does.
- How the pivot is held at its two positions.
- The exact switch model. The published travel and force match Kailh's PG1316 "notebook" family **(inferred)**.
- How the lid is held open (a friction hinge is likely).

**Next check:** when SlashVibe publishes its source code (expected by mid-December 2026), read the protocol and SDK docs. That should answer the questions about the contacts, the button and the key behavior.

---

## Sources
- [slashvibe.ai](https://slashvibe.ai/)
- [Kickstarter campaign](https://www.kickstarter.com/projects/loda/slashvibe), its [FAQ](https://www.kickstarter.com/projects/loda/slashvibe/faqs), [updates](https://www.kickstarter.com/projects/loda/slashvibe/posts) and [comments](https://www.kickstarter.com/projects/loda/slashvibe/comments)
- YouTube: [brand film](https://www.youtube.com/watch?v=R0rtMJmhr_g), [agents demo](https://www.youtube.com/watch?v=6KpWEKje6bg), [to-do demo](https://www.youtube.com/watch?v=FI3O29v640M), [meeting demo](https://www.youtube.com/watch?v=4koQzkaaAcg)
- [The Gadgeteer, Nov 15, 2026](https://the-gadgeteer.com/2026/11/15/slashvibe-open-source-ai-agent-desk-controller/)
- [Freeyork](https://freeyork.org/technology/slashvibe-voice-controller/), [Gadget Flow](https://thegadgetflow.com/blog/slashvibe-gives-your-ai-tools-their-own-spot-on-the-desk/), [Gadgetify](https://www.gadgetify.com/slashvibe-ai-agent-display-with-detachable-controller/)
- SlashVibe's teardown photo on X (Oct 12, 2026), via Nico's screenshot
