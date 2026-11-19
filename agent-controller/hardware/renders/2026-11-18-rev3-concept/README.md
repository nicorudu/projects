# 2026-11-18 — rev 3 concept model

The whole device as a 3D model, with every part where the blueprint puts it.

| File | What it shows |
|---|---|
| `01-device-open.png` | Docked, screen open |
| `02-block-swung-out.png` | Desktop position: the joystick block swung out 90° |
| `03-controller-off-dock.png` | Controller lifted off; the charge contacts on the base's front face |
| `04-closed.png` | Lid closed |
| `05-xray.png` | Shells see-through, every part labeled |
| `06-xray-top.png` | The same from straight above, lid removed |
| `07-exploded-dock.png` | Lid and base pulled apart, labeled |
| `08-exploded-controller.png` | Key section and joystick block pulled apart, labeled |
| `overlaps.txt` | The automatic fit check. It lists any two parts that occupy the same space. Empty means none do. |

- Made by [`../../cad/rev3-pivot/concept.py`](../../cad/rev3-pivot/concept.py). Rerun it after changing a number: `xvfb-run -a python3 concept.py`.
- It is a concept model, **not print-ready**. Part sizes come from datasheets and listings. The print model comes after the real parts are measured (milestone M7a).
- What the model settled and the tight spots it found: [blueprint rev 3](../../../docs/agent-controller-v0-blueprint.md) §4.7.
