# dock_display — display and touch test (M4 bench step 2)

Checks the 4.0" MSP4031 module (ST7796S display over SPI, FT6336U touch over I2C) on the dock board. Pins follow [blueprint §5.1](../../../docs/agent-controller-v0-blueprint.md).

**State: written and compiled on 2026-11-26. Not flashed yet** (waiting for the jumper wires).

## Wiring (12 wires)

Unplug USB before wiring. The module's pins are numbered 1–14 on its silkscreen.

| Module pin | Label | Dock board pin | Note |
|---|---|---|---|
| 1 | VCC | 5V | LCDWIKI recommends 5 V; at 3.3 V the backlight is dimmer |
| 2 | GND | GND | |
| 3 | LCD_CS | GPIO10 | |
| 4 | LCD_RST | GPIO14 | |
| 5 | LCD_RS | GPIO9 | This is the data/command pin (DC) |
| 6 | SDI(MOSI) | GPIO11 | |
| 7 | SCK | GPIO12 | |
| 8 | LED | GPIO8 | Backlight, dimmed by PWM |
| 9 | SDO(MISO) | not connected | Nothing is read back from the display |
| 10 | CTP_SCL | GPIO2 | |
| 11 | CTP_RST | GPIO5 | New in this test; added to blueprint §5.1 |
| 12 | CTP_SDA | GPIO1 | |
| 13 | CTP_INT | GPIO4 | |
| 14 | SD_CS | not connected | Leave the SD card slot empty |

Never wire anything to GPIO35, 36 or 37.

## Check before the first power-up
The module runs on 5 V and the board's pins are 3.3 V. LCDWIKI says the module has a level converter, but it gives no number for the touch pins. So check once with the multimeter:

1. Connect **only** VCC → 5V and GND → GND. Plug in USB.
2. Measure CTP_SDA, CTP_SCL and CTP_INT (module pins 12, 10, 13) against GND.
3. **About 3.3 V or lower: fine, wire the rest.** About 5 V on any of them: stop and tell Claude; those pins then need a different hookup.

## Build and flash
```
FQBN=esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi
PORT=/dev/cu.usbmodem5C850305191
arduino-cli compile -b $FQBN --build-path <a folder outside the repo> .
arduino-cli upload  -b $FQBN -p $PORT --input-dir <that folder> .
```
Serial output is at 115200 baud.

## What it does, and what passes
| Step | What you should see | Pass when |
|---|---|---|
| Touch chip | Serial: `i2c scan: 0x38` and `chip id 0x64` | The chip answers at 0x38 |
| Backlight | A white screen fades from dark to full in 1 s | The fade is smooth |
| Fills | Full red, then green, then blue | Each color is right and covers the whole screen |
| Test card | 8 bars left to right: red, green, blue, yellow, cyan, magenta, white, black. Below: a gray ramp, black on the left. A thin white line on all four edges | Colors and order match; the white line shows on every edge; landscape, 480 × 320 |
| Corners | Touch the screen, then tap each white square in turn (top-left, top-right, bottom-right, bottom-left). Each turns green | 4 of 4, then a green frame and `RESULT: PASS (touch)` |
| Drawing | Drag a finger; yellow dots follow it | The line sits under the finger, with no gaps |

Serial also prints how long a full-screen fill takes, and the raw touch numbers for every tap.

## If something is wrong
Change one setting at the top of `dock_display.ino` and flash again.

| What you see | Change |
|---|---|
| Red and blue are swapped | `COLOR_ORDER_BGR 0` |
| Colors look like a photo negative | `INVERT_COLORS 0` |
| The picture is upside down | `ROTATION 3` |
| The screen stays dark, but serial runs | `BL_ACTIVE_HIGH 0`, then check the LED wire |
| The yellow dot lands away from the finger | Send Claude the `touch down: raw …` lines; it sets `TOUCH_SWAP_XY` / `TOUCH_FLIP_X` / `TOUCH_FLIP_Y` |
| Speckles or torn colors | Lower `SPI_HZ` to `10000000UL`, shorten the wires |
| `no chip at 0x38` | Check CTP_SDA, CTP_SCL, CTP_RST, VCC and GND |

Not confirmed until it runs on the real module: the color inversion setting, which way up the picture is, the touch direction, and the backlight polarity. The settings above cover each one.
