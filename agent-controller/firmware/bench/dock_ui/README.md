# dock_ui — the real screens on the dock display (M4 bench step 3)

Runs `AgentUI`, the same screen library as the simulator, on the ESP32-S3 with the ST7796S display.

**State: compiles for the dock board (665 kB, 50% of the app space). Not flashed or run on hardware yet.** Do `dock_display` first; it proves the wiring.

## Build and flash
```
FQBN=esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi
PORT=/dev/cu.usbmodem5C850305191
arduino-cli compile -b $FQBN --library ../../lib/AgentUI --build-path <a folder outside the repo> .
arduino-cli upload  -b $FQBN -p $PORT --input-dir <that folder> .
```
The first build takes a few minutes because it compiles LVGL.

## Before flashing
Copy the settings that worked in `dock_display` to the top of `dock_ui.ino`: `ROTATION`, `COLOR_ORDER_BGR`, `INVERT_COLORS`, `BL_ACTIVE_HIGH`, `SPI_HZ`.

## What you should see
With no Mac attached it steps through the demo screens every 4 seconds: Agents, the list scrolled, Detail, Approval, a toast, Voice, the empty list. They should match the pictures in `firmware/sim/snapshots/`.

It also accepts protocol messages as JSON lines on the serial port (115200 baud); the first one stops the demo. The real USB link with proper framing comes later in M4.

`demo_messages.h` is generated from `firmware/sim/fixtures/screens.jsonl`.
