# Wiring

**Source of truth for pins and power wiring:** [blueprint §4](../../docs/agent-controller-v0-blueprint.md#4-pin-maps). It covers the dock pin map (ESP32-S3 DevKitC), the controller pin map (XIAO ESP32S3), and the controller power path.

This folder holds what you draw or photograph while building:

| File | What |
|---|---|
| `dock-wiring.png` | Dock wiring diagram (draw once the breadboard version works) |
| `controller-wiring.png` | Controller wiring diagram |
| `YYYY-MM-DD-what.jpg` | Photos of the breadboard and finished harness, e.g. `2026-11-18-dock-breadboard.jpg` |

**Rules that are easy to forget**
- Plug the Mac into the DevKitC's **native USB** port, not the UART/COM port.
- Controller slide switch **OFF** whenever the XIAO's own USB-C is plugged in.
- Never wire to GPIO35–37 on the dock board; the PSRAM uses them.
