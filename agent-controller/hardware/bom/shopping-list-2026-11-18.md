# Shopping list — 2026-11-18 (rev 3)

What to buy now. It covers the rev 3 design and a second audit of everything the build steps need. The full parts list with every status is [BOM.csv](BOM.csv).

- Prices are estimates, not quotes.
- "Search for" is the phrase to type into the store. Match the spec, not a brand.
- When something is ordered, change its status in the BOM to `ordered`.

---

## 1. New: buy these

None of these were on a list you have ordered from.

| ID | Item | Spec to match | Qty | Where | About | Why |
|---|---|---|---|---|---|---|
| C10 | Tactile push buttons | 6 × 6 mm, through-hole, assortment with several button heights, must include 5 mm | 1 kit | Amazon | $7 | The green button and the pivot sensor |
| C11 | Battery lead connectors | JST-PH 2.0 mm, 2-pin, plug + socket pigtail pairs | 1 pack (10 pairs) | Amazon | $7 | The battery plugs into the charger instead of being soldered live |
| C12 | Ceramic capacitors | Assortment that includes 0.1 µF (100 nF) | 1 kit | Amazon | $8 | One steadies the battery reading |
| S6 | Jumper wires | Dupont, 20 cm, 120 pieces: male-male, male-female and female-female | 1 kit | Amazon | $7 | The display and the dock board both have male pins |
| T8 | USB-C power meter | Inline USB-C voltage and current tester | 1 | Amazon | $12 | Measures what the dock draws while the controller charges |
| T9 | Breadboards | 830-point, pack of 2 or 3 | 1 pack | Amazon | $8 | The controller needs its own board while the dock stays wired |

**Subtotal: about $49.**

**C11, read before use.** Battery plugs are not wired the same way by every seller. Before plugging the battery into anything, check with the multimeter which pin is +.

---

## 2. Still on the list from Nov 11: buy any you haven't ordered

The repo doesn't know which of these you ordered. Skip the ones you did.

| ID | Item | Spec to match | Qty | Where | About |
|---|---|---|---|---|---|
| C1 | Seeed XIAO ESP32S3 | Plain, **not** "Sense". Seeed part 113991114. | 2 | DigiKey `1597-113991114-ND` | $7.49 each |
| C2 | Adafruit Mini Analog Thumbstick | Product #5628, Joy-Con style | 2 | DigiKey `1528-5628-ND`, or adafruit.com | $4.50 each |
| C7 | TP4056 charger boards | **USB-C**, **with protection** (the board has two extra pads marked OUT+ and OUT−) | 1 pack | Amazon | $7 |
| C9 | Resistor kit | 1/4 W, 1%, metal film. Must include 10 kΩ, 22 kΩ, 100 kΩ and 150 kΩ. | 1 kit | Amazon | $8 |
| D7 | Magnets | Neodymium discs, 6 mm wide × 2 mm thick, 20 or more | 1 pack | Amazon | $6 |
| S4 | Pin header strips | 2.54 mm, male, 40-pin, breakaway | 1 pack | Amazon | $6 |

**Subtotal: about $51** if none were ordered, plus DigiKey shipping.

- **C1:** DigiKey lists this board as shipped without headers installed. S4 covers that.
- **C2:** buy two. The pins are tiny and easy to damage.

---

## 3. Check your drawers: buy only what's missing

| ID | Item | Spec | About | Why |
|---|---|---|---|---|
| T6 | Digital calipers | 150 mm | $15 | Every "measure it" step depends on them. Nothing is printed before the parts are measured. |
| T7 | Hex key | 1.5 mm | $6 for a small set | Fits the M2 socket-cap screws. Check whether the screw kit came with one. |
| T10 | Second USB-C data cable | USB-C to USB-C, data (not charge-only) | $8 | The dock and the controller board are both plugged into the Mac during flashing |
| T11 | Flush cutters | Small side cutters | $7 | Trimming leads. Check whether the soldering kit includes a pair. |
| S7 | Super glue | Gel type | $5 | Fixes the magnets in their pockets |
| S8 | Foam tape | Double-sided, about 1 mm thick | $6 | Holds the battery, seals the speaker and the mics |
| S9 | Rubber feet | Stick-on, about 8 mm, 4 or more | $5 | Stops the dock sliding. Optional. |

**Subtotal: about $52** if all are missing.

Also check that your wire strippers have a notch for 28 AWG wire. If not, a pair that does is about $10.

---

## 4. Totals

| Group | About |
|---|---|
| 1. New | $49 |
| 2. From Nov 11, if none were ordered | $51 |
| 3. Drawer items, if all are missing | $52 |
| **Worst case** | **$152** plus DigiKey shipping |

---

## 5. Not needed now

- **A different connector, switches or battery.** The 2-pin connector, the Choc switches and the 1000 mAh battery all stay.
- **Paint and sandpaper.** Only if you choose the painted finish. That decision waits until the shell is printed.
- **Green filament or paint for the green button.** Decide when the shell is printed.
- **More filament.** One spool of PETG is enough.

---

## 6. What the second audit caught

These were missing from earlier lists:

| Item | How it was missed |
|---|---|
| C11 battery lead connectors | The blueprint joined the battery to the charger but never said how |
| C12 capacitors | The battery reading uses high-value resistors; the board's input needs a small capacitor to read them steadily |
| T8 USB-C power meter | The blueprint says to measure the dock's current but listed nothing to measure it with |
| T9 breadboards | The dock was planned across both kit breadboards, which left none for the controller |
| S6 jumper kit | Changed from "check" to "buy". The breadboard kit only lists 40 jumpers. |
| T10, T11 | Two cables are needed at once; lead trimming needs cutters |

Sources for the checks: [DigiKey, XIAO ESP32S3](https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/113991114/19285530), [Adafruit #5628](https://www.adafruit.com/products/5628).
