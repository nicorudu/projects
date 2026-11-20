# Shopping list — 2026-11-19

What is still missing after checking Nico's order screenshots (AliExpress and Amazon, sent 2026-11-19) against the parts list, plus what he confirmed in chat the same day. It replaces the [2026-11-18 list](shopping-list-2026-11-18.md).

- The full parts list with every status is [BOM.csv](BOM.csv).
- **Every line names one exact product and one exact quantity** (added 2026-11-19, late). Nico orders exactly what is written here.
- "Must match" is the check to make on the listing before paying, in case the seller has changed it.
- Prices are estimates, not quotes.

---

## 1. Buy these: not ordered yet

Quantity is **1** of each. Each one is a kit or pack that holds more pieces than the build uses.

| ID | Exact product | Qty | Must match | About | What the build uses |
|---|---|---|---|---|---|
| C9 | [Geekstory 1460 Pcs 1/4 W 73 Values 1% Metal Film Resistor Assortment Kit, 1 Ω–1 MΩ](https://www.amazon.com/Precision-Electronic-Assortment-1ohm-1Mohm-Geekstory/dp/B079FP5WD9) (Amazon ASIN B079FP5WD9) | 1 kit | 1/4 W, 1%, metal film. The value list must show 10K, 22K, 100K and 150K. | $12 | 2 × 100 kΩ, 1 × 150 kΩ, 1 × 10 kΩ, 1 × 22 kΩ |
| C10 | [Hilitchi 200-Pcs 6 × 6 mm Tactile Push Button Switch Assortment Kit, 10 values, 4 pins](https://www.amazon.com/Hilitchi-200-Pcs-Tactile-Momentary-Assortment/dp/B071KX71SV) (ASIN B071KX71SV) | 1 kit | 6 × 6 mm body, 4 pins, through-hole. Heights 4.3 to 13 mm, including 5 mm. | $9 | 2 buttons: the green button and the pivot sensor |
| C11 | [10 Pairs JST-PH 2.0 2-Pin Male and Female Connector, silicone cable, 10 cm](https://www.amazon.com/10Pairs-Connector-Silicone-Battery-Inductrix/dp/B0D4MDNZ9D) (ASIN B0D4MDNZ9D) | 1 pack | "JST-PH 2.0", 2 pin, **both** male and female halves in the pack. Not "JST-XH", not "1.25 mm". | $8 | 1 socket half, soldered to the charger |
| C12 | [500 PCS Monolithic Ceramic Capacitor Assortment Kit with box, 0.1 µF–10 µF, 10 values, 50 V](https://www.amazon.com/Monolithic-Assortment-0-1uf-10uf-Multilayer-Electronic/dp/B0CH31DBNL) (ASIN B0CH31DBNL) | 1 kit | Must include 0.1 µF (printed "104"), through-hole, 50 V | $10 | 1 × 0.1 µF |
| T8 | [Plugable USB-C Power Meter Tester, model USBC-VAMETER3](https://plugable.com/products/usbc-vameter3) | 1 | Model number USBC-VAMETER3. It passes USB data, so the dock still talks to the computer while being measured. | $30 | Measures the dock's current with and without the controller charging |

**Subtotal: about $70.** The meter is $30 of that; the earlier $12 estimate was for a generic meter.

**C11, read before use.** Battery plugs are not wired the same way by every seller. Before plugging the battery into anything, check with the multimeter which pin is +.

---

## 2. Buy only if needed

Check the drawer first. Quantity is **1** of each unless the line says otherwise.

| ID | Exact product | Qty | Must match | About | Buy it if |
|---|---|---|---|---|---|
| S6 | ELEGOO 120 pcs Multicolored Dupont Wire kit (part EL-CP-004) | 1 kit | 20 cm; 40 male-male, 40 male-female, 40 female-female | $7 | The jumpers that came with the breadboards are all male-to-male. The display and the dock board both have male pins. |
| T6 | Neiko 01407A Electronic Digital Caliper, 0–6 in / 0–150 mm, stainless steel (Amazon ASIN B000GSLKIW) | 1 | Range 150 mm, reads to 0.01 mm | $20 | You don't own calipers. Nothing is printed before the parts are measured. |
| T10 | Amazon Basics USB-C to USB-C 2.0 cable, 6 ft | 1 | USB-C on both ends, and the listing must state data transfer (480 Mbps). Not "charge only". | $8 | You have only one USB-C data cable. Two boards are plugged into the computer during flashing. |
| T11 | Hakko CHP-170 Micro Cutter | 1 | Flush cut, rated to 16 AWG copper | $8 | The soldering kit has no small flush cutters |
| S7 | Gorilla Super Glue Gel, 20 g, clear (part 7700104) | 1 | "Gel". Not the liquid kind, which runs. | $7 | You have no gel super glue. It fixes the magnets in their pockets. |
| S8 | Scotch-Mount Indoor Double-Sided Mounting Tape 110H, 1/2 in × 80 in, white | 1 roll | Foam, double-sided, 1/16 in (1.6 mm) thick | $5 | You have no foam mounting tape. It makes the speaker and mic gaskets. **It does not go under the battery** (see below). |
| S9 | 3M Bumpon SJ5302, clear | 1 pack, 4 feet used | 7.9 mm across, 2.2 mm tall, self-adhesive | $6 | You want the dock not to slide. Optional. |
| C1 | Seeed Studio XIAO ESP32S3, Seeed part 113991114 (DigiKey `1597-113991114-ND`) | 1 | Plain. **Not** "Sense", not "Plus". | $8–10 | You want a spare. One is enough (see section 4). |
| T7 | 1.5 mm hex key | 1 | Marked 1.5 mm or H1.5 | $6 | The 26-in-1 screwdriver set has no H1.5 bit |

**S8 and the battery.** Earlier lists said foam tape also holds the battery. It can't: the battery has 1.0 mm to spare under the switch pins, and foam tape is 1.6 mm thick. The battery sits on the floor and the printed guard sheet above it keeps it in place. If it rattles, a strip of the cloth tape (S11, already ordered) goes over it.

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
| C2 | Adafruit Mini Analog Thumbstick, product #5628. The 2026-11-18 list said quantity 2, and Nico ordered what the list said. One is used; the second is a spare. |
| T3 | Breadboards with jumpers |
| C3, C4 | Choc switches and keycaps (keeb.io) |

**Check when these arrive**
- **C7 chargers:** the board should have six pads marked IN+, IN−, B+, B−, OUT+ and OUT−. That is the protected kind. If it only has four, tell Claude; the wiring changes slightly.
- **T12 screwdriver set:** look for a hex bit marked H1.5. It fits the M2 screws. If there isn't one, buy T7 from section 2.
- **D1 and X7:** two different ESP32-S3 boards. Measure both; the shell is sized around the one that goes in the dock.
- **C6 battery:** check that its plug fits the C11 socket before soldering the socket to the charger.

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
