# Dock simulator

The dock's screens in a window on the Mac. It compiles the same screen library the dock does (`firmware/lib/AgentUI`), so what you see here is what the real display will draw.

## Build (once, and after changing the screens)
Needs `arduino-cli lib install lvgl ArduinoJson` and `brew install sdl2` (both done on the Mac Mini on 2026-11-26).
```
cd firmware/sim
make
```

## Run it with your real sessions
```
cd software/companion-app && source .venv/bin/activate
python -m companion                    # terminal A
python ../../tools/sim_bridge.py       # terminal B: opens the window
```
Click the window so it has the keyboard.

| Key | Control |
|---|---|
| ↑ ↓ ← → | Stick |
| `s` | Send |
| `c` | Cancel |
| `v` | Voice (press = down, press again = up) |
| `g` | Green button |
| Esc | Quit |

The window title shows the status light ("LED: waiting"). If the app isn't running, the window says "Connecting..." and connects by itself when the app starts. `--zoom 1` makes the window the display's real pixel size (480 × 320); the default is double.

## Pictures of every screen
```
make snapshots
```
writes PNG files to `snapshots/`, one per screen, from `fixtures/screens.jsonl`. The fixtures are made by `python tools/sim_fixtures.py` from the companion app's own view builder, so they are exactly what the app sends.

## How it is wired
```
companion app  ⇄  WebSocket  ⇄  tools/sim_bridge.py  ⇄  one JSON message per line  ⇄  agent-sim
```
`main.cpp` is the only simulator-specific code: the SDL window, the keyboard, the heartbeat and the picture writer. Everything drawn comes from `AgentUI`.
