# Firmware

Started 2026-11-26 with one bench sketch:

- `bench/dock_hello/`: prints the chip, flash size and PSRAM size. Passes on the dock board (16 MB flash, 8 MB PSRAM).
- Build: `arduino-cli compile -b esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi` (ESP32S3 Dev Module, Flash Size = 16 MB, PSRAM = OPI PSRAM). Needs `arduino-cli` and the Espressif `esp32:esp32` core.

The rest is not written yet. Planned layout (details in [blueprint §8](../docs/agent-controller-v0-blueprint.md#8-firmware-layout-arduino-framework-two-targets)):

```
firmware/
  common/       shared protocol definitions
  dock/         ESP32-S3 N16R8 DevKitC: display, touch, USB + Wi-Fi transports, ESP-NOW relay, audio out, LED
  controller/   XIAO ESP32S3: keys, stick, mics, battery, Wi-Fi / ESP-NOW transports, sleep
```

Wi-Fi credentials live in `config.h`, which is git-ignored. Commit `config.h.example` with placeholders instead.
