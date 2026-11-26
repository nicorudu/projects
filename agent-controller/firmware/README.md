# Firmware

Built with **arduino-cli** (ESP32 core 4.0.0) for the boards and a **Makefile** for the desktop simulator. This replaced the earlier PlatformIO plan on 2026-11-26.

```
firmware/
  lib/AgentUI/        the screens (LVGL 9): one library, compiled by both the dock and the simulator
  sim/                desktop simulator: the screens in a window on the Mac, plus PNG snapshots
  bench/dock_hello/   board check: chip, flash and PSRAM size. Passed on the dock board.
  bench/dock_display/ display + touch test. Written and compiled, not flashed yet.
  bench/dock_ui/      AgentUI on the real display. Compiles, not flashed yet.
```

Still to write: the dock firmware proper (USB and Wi-Fi links, ESP-NOW relay, sound, LED) and the controller firmware.

Board settings: ESP32S3 Dev Module, Flash Size = 16 MB, PSRAM = OPI PSRAM (`esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi`). Libraries: `arduino-cli lib install lvgl ArduinoJson`.

Wi-Fi credentials live in `config.h`, which is git-ignored. Commit `config.h.example` with placeholders instead.
