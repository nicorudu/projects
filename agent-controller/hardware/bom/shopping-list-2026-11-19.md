# Shopping list — 2026-11-19

What is still missing after checking Nico's order screenshots (AliExpress and Amazon, sent 2026-11-19) against the parts list. It replaces the [2026-11-18 list](shopping-list-2026-11-18.md).

- The full parts list with every status is [BOM.csv](BOM.csv).
- Prices are estimates, not quotes.
- "Spec to match" is what to look for. Match the spec, not a brand.

---

## 1. Buy these: not ordered yet

| ID | Item | Spec to match | Qty | Where | About | Why |
|---|---|---|---|---|---|---|
| C2 | Adafruit Mini Analog Thumbstick | Product #5628, Joy-Con style | 2 | adafruit.com, or DigiKey `1528-5628-ND` | $4.50 each | The joystick. Nothing else on order can stand in for it. |
| C1 | Seeed XIAO ESP32S3, a second one | Plain, **not** "Sense" | 1 | Amazon (Seeed Studio), or DigiKey `1597-113991114-ND` | $8–10 | One is on order. The breadboard one gets header pins; the finished controller needs a bare one, because pins don't fit under the switches. |
| C9 | Resistor kit | 1/4 W, 1%, metal film. Must include 10 kΩ, 22 kΩ, 100 kΩ and 150 kΩ. | 1 kit | Amazon | $8 | Battery level, docked sensing, green button |
| C10 | Tactile push buttons | 6 × 6 mm, through-hole, assortment of heights that includes 5 mm | 1 kit | Amazon | $7 | The green button and the pivot sensor |
| C11 | Battery lead connectors | JST-PH 2.0 mm, 2-pin, plug + socket pigtail pairs | 1 pack | Amazon | $7 | The battery plugs into the charger instead of being soldered live |
| C12 | Ceramic capacitors | Assortment that includes 0.1 µF (100 nF) | 1 kit | Amazon | $8 | One steadies the battery reading |
| S6 | Jumper wires | Dupont, 20 cm, 120 pieces: male-male, male-female and female-female | 1 kit | Amazon | $7 | The display and the dock board both have male pins |
| T9 | Breadboards | 830-point, pack of 3 | 1 pack | Amazon | $9 | No breadboards appear in the orders. The dock and the controller each need one. |
| T8 | USB-C power meter | Inline USB-C voltage and current tester | 1 | Amazon | $12 | Measures what the dock draws while the controller charges |

**Subtotal: about $76.**

**C11, read before use.** Battery plugs are not wired the same way by every seller. Before plugging the battery into anything, check with the multimeter which pin is +.

---

## 2. Buy only if you don't own one

| ID | Item | Spec | About | Why |
|---|---|---|---|---|
| T6 | Digital calipers | 150 mm | $15 | Every "measure it" step depends on them. Nothing is printed before the parts are measured. |
| T10 | Second USB-C data cable | USB-C to USB-C, data (not charge-only) | $8 | The dock and the controller board are both plugged into the computer during flashing |
| T11 | Flush cutters | Small side cutters | $7 | Trimming leads. Check the soldering kit first. |
| S7 | Super glue | Gel type | $5 | Fixes the magnets in their pockets |
| S8 | Foam tape | Double-sided, about 1 mm thick | $6 | Holds the battery, seals the speaker and the mics |
| S9 | Rubber feet | Stick-on, about 8 mm, 4 or more | $5 | Stops the dock sliding. Optional. |

**Subtotal: about $46** if all are missing.

---

## 3. Already on order: nothing to do

Seen in the screenshots:

| ID | Item | Order |
|---|---|---|
| D1 | ESP32-S3 DevKitC-1 N16R8, "KIT C" with an expansion board | AliExpress, Nov 8 |
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
| X7 | A second ESP32-S3 N16R8 board (spare) | AliExpress, Nov 9 |

Ordered from keeb.io (no screenshot): the Choc switches and keycaps (C3, C4).

**Check when these arrive**
- **C7 chargers:** the board should have six pads marked IN+, IN−, B+, B−, OUT+ and OUT−. That is the protected kind. If it only has four, tell Claude; the wiring changes slightly.
- **T12 screwdriver set:** look for a hex bit marked H1.5. It fits the M2 screws. If there isn't one, add a 1.5 mm hex key (about $6).
- **D1 and X7:** two different ESP32-S3 boards. Measure both; the shell is sized around the one that gets used.

---

## 4. No longer needed

- **Pin header strip (S4).** The XIAO order includes five pairs of 7-pin headers, and the mic and amplifier boards arrive with pins soldered.
- **A separate breadboard kit (T3).** The 3-pack in section 1 covers it.

---

## 5. Left out on purpose

Three orders in the screenshots are not for this project and are not in the parts list: the 2.0" TFT display, the DFPlayer Mini MP3 module, and the NFC stickers.

---

## 6. Totals

| Group | About |
|---|---|
| 1. Not ordered yet | $76 |
| 2. If you own none of them | $46 |
| **Worst case** | **$122**, plus shipping for the thumbsticks |

**Fewest orders:** everything is on Amazon except the thumbsticks. Order those from adafruit.com, or from DigiKey together with the second XIAO.
