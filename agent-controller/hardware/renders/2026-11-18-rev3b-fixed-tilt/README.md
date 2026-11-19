# 2026-11-18 — rev 3b: the fixed-tilt option

An **option**, not the chosen design: the same base and controller as rev 3, with the screen in a rigid wedge at 60° instead of a folding lid. What changes and how to decide: [docs/option-fixed-tilt.md](../../../docs/option-fixed-tilt.md).

| File | What it shows |
|---|---|
| `01-tilt-device.png` | The device from the front |
| `02-tilt-block-swung-out.png` | Desktop position: the joystick block swung out |
| `03-tilt-back.png` | From behind: sound and air slots, USB-C sockets |
| `04-compare.png` | The folding version and this one side by side |
| `05-tilt-xray.png` | Shells see-through, parts labeled |
| `06-tilt-xray-side.png` | See-through from the right side: the wedge's shape and what is inside |
| `07-tilt-exploded.png` | Base and screen housing pulled apart, labeled |
| `overlaps.txt` | The automatic fit check. Empty means no two parts overlap. |

- Made by [`../../cad/rev3b-fixed-tilt/concept_tilt.py`](../../cad/rev3b-fixed-tilt/concept_tilt.py): `xvfb-run -a python3 concept_tilt.py`.
- Concept model, **not print-ready**.
