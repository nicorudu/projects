# AI Agent Controller — complete plan (rev 3)

Written 2026-11-18, after re-checking every photo in the chat and everything public about SlashVibe. Where this plan disagrees with anything written before it, **this plan wins**.

- What the reference product is: [research/slashvibe-reference.md](research/slashvibe-reference.md)
- How to build ours: [agent-controller-v0-blueprint.md](agent-controller-v0-blueprint.md) (rev 3)
- How the code is organized: [architecture.md](architecture.md)

---

## 1. Goal

Build a personal copy of the SlashVibe idea that is as close to the real product as a 3D printer and off-the-shelf parts allow.

- A desk dock with a fold-flat screen.
- A detachable controller with three keys, a thumbstick on a pivoting block, and close-talk mics.
- A companion app that shows every AI agent session, lets you approve requests, and takes voice.

**v0 is done when all of this is true:**
1. The dock shows live Claude Code sessions over one USB-C cable.
2. The controller works docked, handheld, and with the joystick block swung out.
3. You can approve or reject a real Claude Code request from the device.
4. You can hold Voice, speak, see the text on the dock, and press Send or Cancel.
5. The controller charges when docked and lasts a workday off the dock.
6. The printed shell has the reference layout: ribbed base, flush key plates, wide stick cap, mics on the block's end face, pivot.

Credit SlashVibe as the inspiration on the website. Don't put their wordmark on the print.

---

## 2. Where we stand (2026-11-18)

| Area | State |
|---|---|
| Companion app: live Claude Code status and approvals | **Working.** Tested on the Mac Mini with a fake device (M0, M1). |
| Voice | Planned and tabled. The engine will be a copy of Wispr Faux (M2). |
| Dock and controller firmware | Not started |
| Screen design | Not started |
| Shell | Rev 2 concept only. **Rev 3 replaces it** (pivot, key order, key size). |
| Parts | Most were ordered Nov 8–11. Arrival not confirmed. See §6. |

---

## 3. What the re-check changed

| # | Change | Why |
|---|---|---|
| 1 | **The joystick block pivots 90°.** | The reference does. I wrongly ruled this out on Nov 11; Nico's photo shows it. |
| 2 | Key order is **Cancel / Send / Voice**, with Voice beside the joystick. | Photos of real units |
| 3 | Keys are **large plates** (about 25 × 36 mm on ours), not keyboard-size caps. | Teardown and close-ups |
| 4 | The stick's **click is not used**. Stick right opens, stick left goes back, Send confirms. | The reference stick has no click |
| 5 | A **green button** is added on the joystick block. | Teardown shows a small switch with a green cap |
| 6 | The controller **attaches to the base's front face**. There is no tray around it. | Reference layout; a tray would block the pivot |
| 7 | The controller **always talks to the dock** by radio. Only the dock talks to the computer, by USB or Wi-Fi. | Same as the reference; better battery life; less firmware |
| 8 | Screens copy the reference: usage header, status rows, a detail page, and a voice bubble. | Demo videos |

Kept as they were: both boards, the display, the amp and speaker, the mics, the battery, the charger and the magnetic connector. **Nothing already bought is wasted.**

---

## 4. Feature by feature

| Reference feature | Ours in v0 | Notes |
|---|---|---|
| Fold-flat screen on a ribbed base | Yes | 4.0" 480 × 320 touch panel. Our screen is lower resolution than theirs looks. |
| Detachable wireless controller | Yes | ESP-NOW radio in place of their 2.4 GHz link |
| Pivoting joystick block | Yes | Printed pivot. A magnet holds it in line; a printed click holds it at 90°. |
| Three large key plates | Yes | Printed plates on Choc switches. Travel is 3 mm, against their 1.8 mm. |
| Wide flat stick cap, four ticks | Yes | Printed cap on a Joy-Con-style stick |
| Dual close-talk mics on the end face | Yes | 2 × INMP441 |
| 2 W speaker under the grille | Yes | 40 mm round speaker |
| Charges when docked | Yes | 2 contacts (power only), against their 4 |
| USB-C power and data | Yes | Also Wi-Fi, to compare speed |
| Agent list with statuses and alert sound | Yes | Already working in the app |
| Select a session → its window comes forward | Yes | macOS first |
| Approve requests on the device | Yes | Already working |
| Voice with cleanup, Send / Cancel | Yes | Wispr Faux as the engine |
| Usage header (spend, 5h / 7d) | Try | Depends on what Claude Code exposes; research item |
| To-dos by voice (`/todo`) | Later | After v0 |
| Meeting assistant (`/meeting`) | Later | After v0 |
| SDK for custom screens | Later | Our screens are templates first |
| Aluminium shell, soft-touch finish | No | Printed PETG. Sanding and paint are optional. |
| 20+ agents | Partly | Claude Code first, then Cursor and the chat apps through focus and paste |

**Size, honestly.** The reference is 105 × 89 × 21 mm. Ours will be about 124 × 112 × 35 mm closed. Our display module is 108 mm wide, the dev boards are tall, and the battery is 8 mm thick.

---

## 5. Milestones

Work is split three ways: **Cloud** (Claude in this chat), **Mac** (Claude Code on the Mac Mini), and **Bench** (Nico with parts on the desk, guided step by step).

| # | What | Where | Needs parts? | Pass when | State |
|---|---|---|---|---|---|
| M0 | App restructure, protocol, fake device | Cloud | No | Tests pass | Done |
| M1 | Claude Code status and approvals | Cloud + Mac | No | Real approval from the fake device | Done |
| **M1b** | Reference controls in the app: right opens, left goes back, focus follows selection, detail page, IDLE / READY rows, green button, no stick click | Cloud | No | Fake device behaves like the demo video | Done 2026-11-26 (66 tests; checked on the Mac Mini with real sessions) |
| M2 | Voice through a copy of Wispr Faux: dock review, Send / Cancel | Cloud + Mac | No | Dictate into Claude Code from the fake device | Tabled until Nico restarts it |
| M3 | Screens in the desktop simulator (LVGL, 480 × 320), styled like the reference | Cloud | No | Screens match the reference screenshots side by side | Done 2026-11-26: all screens run in the simulator and compile for the dock; looked over by Nico |
| M4 | Dock on the breadboard: display, touch, speaker, LED, USB and Wi-Fi links | Bench | Yes | Real sessions on the real screen | Waits for parts check |
| M5 | Controller on the breadboard: keys, stick, button, LED, mics, battery, ESP-NOW | Bench | Yes | Every input reaches the Mac through the dock | After M4 |
| M6 | USB vs Wi-Fi speed test and battery test | Bench | Yes | Numbers recorded; default link chosen | After M5 |
| **M7a** | Measure every part with calipers | Bench | Yes | Measurement sheet filled in | With M4 |
| **M7b** | Rev 3 CAD plus four test prints: pivot, key plate, stick cap, hinge | Cloud + Bench | Printer | Each test piece works by hand | After M7a |
| **M7c** | Full print, wiring, assembly | Bench | Yes | Docks, charges, pivots, lid folds | After M7b |
| M8 | Polish: usage header, alert sounds, Work Brief, Cursor and chat apps | Cloud + Mac | No | Blueprint test plan passes | After M7c |
| Later | To-dos, meetings, custom screens, Windows | — | — | — | v1 |

**Order that keeps everyone busy:** M1b and M3 need no parts, so they run while Nico confirms what has arrived. M4 starts the day the display and the dock board are both in hand.

---

## 6. Parts: what to check and what to add

**The list to shop from is [shopping-list-2026-11-19.md](../hardware/bom/shopping-list-2026-11-19.md).** It was checked against the real orders on 2026-11-19 and replaces the tables below, which are kept as history.

The full list with order status is in [BOM.csv](../hardware/bom/BOM.csv). The repo's order statuses are from Nov 11, so **please confirm what you actually ordered and what has arrived.**

### A. Still marked "to order" on Nov 11. Confirm each.
| ID | Part | Needed for |
|---|---|---|
| C1 | Seeed XIAO ESP32S3 (plain) × 2 | The controller |
| C2 | Adafruit #5628 mini thumbstick × 2 | The stick |
| C7 | TP4056 USB-C charger with protection | Charging the controller |
| C9 | Resistor kit that includes 10 kΩ, 22 kΩ, 100 kΩ and 150 kΩ | Battery level, docked sense, green button |
| D7 | 6 × 2 mm neodymium magnets, 20 or more | Docking, pivot, lid |
| S4 | 2.54 mm breakaway header strip | Breadboard XIAO |

### B. New in rev 3
| ID | Part | Spec | Why |
|---|---|---|---|
| C10 | Tactile push buttons | 6 × 6 mm, through-hole, 5 mm tall, pack of 10 or more | Two are used: the green button on the joystick block, and the sensor that tells whether the block is swung out |

### C. Check you have these. Earlier lists missed them.
| ID | Item | Why |
|---|---|---|
| T6 | Digital calipers, 150 mm | Every "measure it" step depends on them |
| T7 | 1.5 mm hex key | For the M2 socket-cap screws. Check whether the screw kit includes one. |
| S7 | Super glue (gel) | Fixing magnets in their pockets |
| S8 | Double-sided foam tape | Speaker and mic gaskets. Not under the battery: there is no room for it. |
| S9 | Stick-on rubber feet, 4 or more | So the dock doesn't slide. Optional but cheap. |
| T10 | A second USB-C data cable | The dock and the controller board are both plugged in during flashing |
| T11 | Flush cutters | Trimming leads. Check whether the soldering kit includes a pair. |

### D. Not needed
- A 4-pin connector. Ours stays 2-pin for v0.
- New switches. The Choc V1 switches stay.
- A different battery. See the option in §7.
- The plain keycaps are still used on the breadboard.

### E. Added by the second audit (2026-11-18, evening)
| ID | Part | Why |
|---|---|---|
| C11 | JST-PH 2.0 mm 2-pin pigtails | The battery plugs into the charger instead of being soldered live |
| C12 | Ceramic capacitor kit that includes 0.1 µF | Steadies the battery reading |
| S6 | Jumper kit with male-male, male-female and female-female wires | Moved from "check" to "buy". The display and dock board both have male pins. |
| T8 | USB-C power meter | Measures the dock's current while the controller charges |
| T9 | Two more 830-point breadboards | The controller needs its own while the dock stays wired |

C10 also changed: buy an assortment of heights, so the right one can be picked after measuring.

---

## 7. Risks and fallbacks

| Risk | What we'd see | Fallback |
|---|---|---|
| A big key plate on one switch wobbles or sticks | Uneven press | The plate hinges at its rear edge and presses the switch like a lever. Tested in M7b before the full print. |
| Ten wires through the pivot wear out | An input drops out after many swings | Silicone wire with a slack loop; the pivot is limited to 90°. If it fails, move the status LED out of the block (8 wires). |
| The 8 mm battery makes the controller thick | Controller about 22 mm tall | Accept it for v0 (it sits flush with our base). Optional: a 5 mm-thick cell later. |
| The wide stick cap rocks instead of sliding | Feels different from the reference | Tune the cap and dish in M7b. Their stick slides 2 mm; ours tilts. |
| Radio audio drops words | Gaps in dictation | Compressed audio, a small buffer, resend on loss. Measured in M6. |
| First word clipped | "…factor the" instead of "Refactor the" | Keep the mics running with a short rolling buffer whenever the controller is awake |
| The screen redraws slowly | Laggy lists | The dock draws from small messages, not streamed pictures. Measured in M4. |
| The lid won't stay open | Lid flops | The lid leans back onto a printed stop at 105°, so gravity holds it. No friction hinge needed. |
| Parts differ from listings | Holes don't line up | Nothing is printed before M7a's measurements |
| SlashVibe's open-source code is AGPL | Copying it would force that license on our code | Learn from how it behaves; write our own code |

---

## 8. Decisions for Nico

1. **Parts status.** Which of the §6 A items did you order, and what has arrived?
2. **The new and missing items** (§6 B and C). OK to order what you don't have?
3. **Voice (M2).** Still on hold. When you restart it, the first question is whether the Wispr Faux copy replaces the original app on the Mac or runs beside it.
4. **Finish.** Raw print, or sand and paint to get closer to the aluminium look? This can wait until M7c.

---

## 9. Rules that still apply
- Every step is committed to GitHub, and [HANDOFF.md](../HANDOFF.md) is updated.
- Every part change goes into the BOM with a status.
- The website is never edited from here.
- The `wispr-faux` repo is never edited.
- Branch first; never commit to `main`.
