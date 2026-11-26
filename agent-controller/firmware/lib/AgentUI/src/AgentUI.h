// AgentUI: the AI Agent Controller's screens.
//
// The companion app decides what is on screen and sends protocol v1 messages (welcome, view,
// patch, toast, led, sound). This library turns them into LVGL objects. It has no hardware
// code, so the dock firmware and the desktop simulator compile exactly the same files.
//
// The host (dock firmware or simulator) must:
//   1. call lv_init(), give LVGL a tick source, and create a 480 x 320 display;
//   2. call agent_ui::begin();
//   3. pass every JSON message from the Mac to agent_ui::handle_message();
//   4. call lv_timer_handler() regularly, from the same task as everything above.
#pragma once

#include <stddef.h>
#include <stdint.h>

#include <lvgl.h>

namespace agent_ui {

constexpr int SCREEN_W = 480;
constexpr int SCREEN_H = 320;

// What the screens need from the host. Any of these may be left null.
struct Host {
  // Send one complete JSON message to the Mac (used for "layout", see protocol/messages.py).
  void (*send)(const char *json, void *ctx) = nullptr;
  // Status light: idle, working, waiting, done, error or recording.
  void (*led)(const char *mode, void *ctx) = nullptr;
  // Play a sound by name ("alert").
  void (*sound)(const char *name, void *ctx) = nullptr;
  void *ctx = nullptr;
};

// Build the UI on the default display. Shows "Connecting..." until the first welcome.
void begin(const Host &host);

// One JSON message from the Mac. Unknown or malformed messages are ignored.
void handle_message(const char *json, size_t len);

// The link came up or went down. While down, a "Disconnected" banner covers the top edge.
void set_connected(bool connected);

// The screen now showing: connecting, home, detail, approval or voice.
const char *screen_name();

}  // namespace agent_ui
