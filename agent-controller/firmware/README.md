# Firmware

Not started. Planned layout (details in [blueprint §8](../docs/agent-controller-v0-blueprint.md#8-firmware-layout-arduino-framework-two-targets)):

```
firmware/
  common/       shared protocol definitions
  dock/         ESP32-S3 N16R8 DevKitC: display, touch, USB + Wi-Fi transports, ESP-NOW relay, audio out, LED
  controller/   XIAO ESP32S3: keys, stick, mics, battery, Wi-Fi / ESP-NOW transports, sleep
```

Wi-Fi credentials live in `config.h`, which is git-ignored. Commit `config.h.example` with placeholders instead.
