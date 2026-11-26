# AgentUI

The AI Agent Controller's screens, drawn with LVGL 9. **One library, two builds:** the dock firmware (arduino-cli) and the desktop simulator (`firmware/sim`) compile these same files.

It has no hardware code. The host creates the LVGL display, then passes in every protocol v1 message from the Mac (`welcome`, `view`, `patch`, `toast`, `led`, `sound`). The library draws; it never decides anything.

| File | What |
|---|---|
| `src/AgentUI.h` | The whole public interface: `begin`, `handle_message`, `set_connected` |
| `src/AgentUI.cpp` | The five screens (Agents, Detail, Approval, Voice, Connecting), the toast and the Disconnected banner |
| `src/ui_theme.h` | Colors, fonts and sizes (blueprint §7.2) |
| `src/ui_text.*` | Text clean-up and time formatting |
| `src/lv_conf.h` | LVGL settings shared by both builds |

## Things to know
- **Needs LVGL 9.6 or newer** and ArduinoJson 7.
- **Screens update in place.** A change redraws only the labels that changed, which matters on a display fed over SPI.
- **Detail scrolling:** the library tells the Mac how far the page can scroll (`layout` message), so the stick stops at the end.
- **Fonts hold ASCII only.** Accented letters are shown without their accent, smart quotes and dashes become plain ones, and emoji become `?`. A custom font with accents is a later job (M8).
- **Voice** is laid out but nothing drives it until M2.
- Touch is not used.
