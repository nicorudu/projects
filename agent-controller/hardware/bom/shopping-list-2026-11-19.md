# Shopping list — 2026-11-19

What is still missing after checking Nico's order screenshots (AliExpress and Amazon, sent 2026-11-19) against the parts list, plus what he confirmed in chat the same day. It replaces the [2026-11-18 list](shopping-list-2026-11-18.md).

- The full parts list with every status is [BOM.csv](BOM.csv).
- Prices are estimates, not quotes.
- "Spec to match" is what to look for. Match the spec, not a brand.

---

## 1. Buy these: not ordered yet

| ID | Item | Spec to match | Qty | Where | About | Why |
|---|---|---|---|---|---|---|
| C9 | Resistor kit | 1/4 W, 1%, metal film. Must include 10 kΩ, 22 kΩ, 100 kΩ and 150 kΩ. | 1 kit | Amazon | $8 | Battery level, docked sensing, green button |
| C10 | Tactile push buttons | 6 × 6 mm, through-hole, assortment of heights that includes 5 mm | 1 kit | Amazon | $7 | The green button and the pivot sensor |
| C11 | Battery lead connectors | JST-PH 2.0 mm, 2-pin, plug + socket pigtail pairs | 1 pack | Amazon | $7 | The battery plugs into the charger instead of being soldered live |
| C12 | Ceramic capacitors | Assortment that includes 0.1 µF (100 nF) | 1 kit | Amazon | $8 | One steadies the battery reading |
| T8 | USB-C power meter | Inline USB-C voltage and current tester | 1 | Amazon | $12 | Measures what the dock draws while the controller charges |

**Subtotal: about $42.** All five are on Amazon.

**C11, read before use.** Battery plugs are not wired the same way by every seller. Before plugging the battery into anything, check with the multimeter which pin is +.

---

## 2. Buy only if needed

| ID | Item | Spec | About | When you need it |
|---|---|---|---|---|
| S6 | Jumper wires with female ends | Dupont, 20 cm, 120 pieces: male-male, male-female and female-female | $7 | If the jumpers that came with your breadboards are all male-to-male. The display and the dock board both have male pins. |
| C1 | A second XIAO ESP32S3 | Plain, **not** "Sense" | $8–10 | Optional spare. One is enough (see section 4). |
| T6 | Digital calipers | 150 mm | $15 | If you don't own a pair. Nothing is printed before the parts are measured. |
| T10 | Second USB-C data cable | USB-C to USB-C, data (not charge-only) | $8 | If you only have one. Two boards are plugged into the computer during flashing. |
| T11 | Flush cutters | Small side cutters | $7 | If the soldering kit doesn't include a pair |
| S7 | Super glue | Gel type | $5 | Fixes the magnets in their pockets |
| S8 | Foam tape | Double-sided, about 1 mm thick | $6 | Holds the battery, seals the speaker and the mics |
| S9 | Rubber feet | Stick-on, about 8 mm, 4 or more | $5 | Stops the dock sliding. Optional. |

---

## 3. Already ordered: nothing to do

Seen in the screenshots:

| ID | Item | Order |
|---|---|---|
| D1 | ESP32-S3 DevKitC-1 N16R8, "KIT C" with an expansion board | AliExpress, Nov 8 |
| X7 | A second ESP32-S3 N16R8 board (Top Tech) | AliExpress, Nov 9 |
| D2 | 4.0" display with capacitive touch (MSP4031) | AliExpress, Nov 8 |
| D3 | MAX98357A amplifier | AliExpress, Nov 8 |
| D4 | 40 mm speakers, 5-pack | AliExpress, Nov 9 |
| D5 | WS2812B LED modules, 10-pack | AliExpress, Nov 8 |
| D6 | Magnetic 2-pin spring connectors, 2 sets | AliExpress, Nov 9 |
| D7 | 6 × 2 mm magnets, 100 | AliExpress, Nov 9 |
| C1 | XIAO ESP32S3 × 1, with five pairs of header pins | AliExpress, Nov 9 |
| C5 | INMP441 mics × 2 (two orders) | AliExpress, Nov 8 and 9 |
| C6 | 1000 mAh battery | Amazon |
| C7 | TP4056 USB-C chargers, 5-pack | AliExpress, Nov 9 |
| C8 | Slide switches, 20-pack | AliExpress, Nov 9 |
| S1 | 28 AWG silicone wire, 10 colors | AliExpress, Nov 8 |
| S2 | M2 inserts and screws kit | AliExpress, Nov 8 |
| S3 | Heat-shrink kit with heat gun | AliExpress, Nov 9 |
| S10, S11 | Solder wire, cloth tape | AliExpress, Nov 9 |
| T1, T2 | Soldering station, multimeter | Amazon |
| T12, T13 | 26-in-1 screwdriver set, wire fixture, dust blower | AliExpress, Nov 9 |

Confirmed by Nico, no screenshot:

| ID | Item |
|---|---|
| C2 | The thumbstick |
| T3 | Breadboards with jumpers |
| C3, C4 | Choc switches and keycaps (keeb.io) |

**Check when these arrive**
- **C7 chargers:** the board should have six pads marked IN+, IN−, B+, B−, OUT+ and OUT−. That is the protected kind. If it only has four, tell Claude; the wiring changes slightly.
- **T12 screwdriver set:** look for a hex bit marked H1.5. It fits the M2 screws. If there isn't one, add a 1.5 mm hex key (about $6).
- **D1 and X7:** two different ESP32-S3 boards. Measure both; the shell is sized around the one that goes in the dock.

---

## 4. Why one XIAO is enough

The earlier lists asked for two XIAO boards: one with header pins for the breadboard, and a bare one for the finished controller, because pins don't fit under the key switches.

The second ESP32-S3 board (X7) removes that need:
- **On the breadboard,** X7 stands in for the controller. It is the same chip, so the same code runs on it; only the pin numbers differ.
- **In the finished controller,** the one XIAO goes in bare.

What this costs:
- The XIAO's own battery pads and antenna are first tested in the final wiring, not on the breadboard.
- There is no spare XIAO if one is damaged while soldering.

X7 can't go inside the controller itself. It is about three times the XIAO's length and has no battery pads.

---

## 5. No longer needed

- **Pin header strip (S4).** The XIAO order includes five pairs of 7-pin headers, and the mic and amplifier boards arrive with pins soldered.
- **Extra breadboards (T9).** The dock board sits on the expansion board that comes with it, so the breadboards are free for the controller.

---

## 6. Left out on purpose

Three orders in the screenshots are not for this project and are not in the parts list: the 2.0" TFT display, the DFPlayer Mini MP3 module, and the NFC stickers.
