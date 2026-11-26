// Desktop simulator for the dock: the AgentUI screens in an SDL window.
//
// It behaves like the dock on its USB link, with one JSON message per line:
//   stdin   messages from the Mac (welcome, view, patch, toast, led, sound, pong, ack)
//   stdout  messages to the Mac   (hello, ping, input, layout)
// tools/sim_bridge.py connects those two pipes to the companion app.
//
// Keys:  arrows = stick   s = Send   c = Cancel   v = Voice (press = down, again = up)
//        g = green button   Esc or closing the window quits
//
// Headless mode, for pictures of every screen:
//   agent-sim --script fixtures/screens.jsonl --out snapshots
// The script is the same JSON lines, plus {"t":"snap","name":"x"} (write x.bmp),
// {"t":"wait","ms":N} (let time pass) and {"t":"link","up":false} (the link drops).

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <chrono>
#include <fstream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include <ArduinoJson.h>
#include <lvgl.h>

#include "AgentUI.h"

namespace {

using Clock = std::chrono::steady_clock;
const auto g_t0 = Clock::now();
uint32_t g_fake_ms = 0;
bool g_use_fake_clock = false;

uint32_t real_ms() {
  return static_cast<uint32_t>(std::chrono::duration_cast<std::chrono::milliseconds>(Clock::now() - g_t0).count());
}
uint32_t tick_cb() { return g_use_fake_clock ? g_fake_ms : real_ms(); }

// ---- link: stdout out, stdin in ---------------------------------------------------------
std::mutex g_out_mutex;
void send_line(const char *json) {
  std::lock_guard<std::mutex> lock(g_out_mutex);
  fputs(json, stdout);
  fputc('\n', stdout);
  fflush(stdout);
}

std::mutex g_in_mutex;
std::vector<std::string> g_in_lines;
bool g_stdin_closed = false;

void stdin_reader() {
  std::string line;
  int c;
  while ((c = fgetc(stdin)) != EOF) {
    if (c == '\n') {
      std::lock_guard<std::mutex> lock(g_in_mutex);
      g_in_lines.push_back(line);
      line.clear();
    } else {
      line += static_cast<char>(c);
    }
  }
  std::lock_guard<std::mutex> lock(g_in_mutex);
  g_stdin_closed = true;
}

// ---- host callbacks ---------------------------------------------------------------------
lv_display_t *g_window = nullptr;
std::string g_led = "idle";

void host_send(const char *json, void *) { send_line(json); }
void host_led(const char *mode, void *) {
  g_led = mode;
  if (g_window) lv_sdl_window_set_title(g_window, ("AI Agent Controller - LED: " + g_led).c_str());
  fprintf(stderr, "[sim] led %s\n", mode);
}
void host_sound(const char *name, void *) { fprintf(stderr, "[sim] sound %s\n", name); }

// ---- inputs -----------------------------------------------------------------------------
uint32_t g_seq = 0;
bool g_voice_down = false;

void send_input(const char *name) {
  char buf[96];
  snprintf(buf, sizeof buf, "{\"v\":1,\"t\":\"input\",\"seq\":%u,\"ts\":%u,\"in\":\"%s\"}", ++g_seq, real_ms(), name);
  send_line(buf);
}

void on_key(lv_event_t *e) {
  switch (lv_event_get_key(e)) {
    case LV_KEY_UP: send_input("up"); break;
    case LV_KEY_DOWN: send_input("down"); break;
    case LV_KEY_LEFT: send_input("left"); break;
    case LV_KEY_RIGHT: send_input("right"); break;
    case 's': case 'S': send_input("send"); break;
    case 'c': case 'C': send_input("cancel"); break;
    case 'g': case 'G': send_input("green"); break;
    case 'v': case 'V':
      g_voice_down = !g_voice_down;
      send_input(g_voice_down ? "voice_down" : "voice_up");
      break;
    case LV_KEY_ESC: _exit(0);
    default: break;
  }
}

// ---- headless display + pictures --------------------------------------------------------
uint16_t g_fb[agent_ui::SCREEN_W * agent_ui::SCREEN_H];  // RGB565, like the real panel

void headless_flush(lv_display_t *disp, const lv_area_t *, uint8_t *) { lv_display_flush_ready(disp); }

bool write_bmp(const std::string &path) {
  const int w = agent_ui::SCREEN_W, h = agent_ui::SCREEN_H;
  const uint32_t row = static_cast<uint32_t>(w) * 3, size = 54 + row * h;  // 480*3 is a multiple of 4
  uint8_t head[54] = {'B', 'M'};
  auto put32 = [&](int at, uint32_t v) { for (int i = 0; i < 4; i++) head[at + i] = static_cast<uint8_t>(v >> (8 * i)); };
  put32(2, size); put32(10, 54); put32(14, 40); put32(18, w); put32(22, h);
  head[26] = 1; head[28] = 24; put32(34, row * h);
  std::ofstream f(path, std::ios::binary);
  if (!f) return false;
  f.write(reinterpret_cast<const char *>(head), 54);
  std::vector<uint8_t> line(row);
  for (int y = h - 1; y >= 0; y--) {  // BMP rows run bottom to top
    for (int x = 0; x < w; x++) {
      const uint16_t p = g_fb[y * w + x];
      const uint8_t r = (p >> 11) & 0x1F, g = (p >> 5) & 0x3F, b = p & 0x1F;
      line[3 * x] = static_cast<uint8_t>((b << 3) | (b >> 2));
      line[3 * x + 1] = static_cast<uint8_t>((g << 2) | (g >> 4));
      line[3 * x + 2] = static_cast<uint8_t>((r << 3) | (r >> 2));
    }
    f.write(reinterpret_cast<const char *>(line.data()), row);
  }
  return true;
}

void pass_time(uint32_t ms) {
  for (uint32_t done = 0; done < ms; done += 20) {
    g_fake_ms += 20;
    lv_timer_handler();
  }
}

int run_script(const std::string &script, const std::string &out_dir) {
  g_use_fake_clock = true;
  lv_display_t *disp = lv_display_create(agent_ui::SCREEN_W, agent_ui::SCREEN_H);
  lv_display_set_buffers(disp, g_fb, nullptr, sizeof g_fb, LV_DISPLAY_RENDER_MODE_DIRECT);
  lv_display_set_flush_cb(disp, headless_flush);

  agent_ui::Host host;
  host.send = [](const char *json, void *) { fprintf(stderr, "[sim] -> %s\n", json); };
  host.led = host_led;
  host.sound = host_sound;
  agent_ui::begin(host);

  std::ifstream in(script);
  if (!in) {
    fprintf(stderr, "can't open %s\n", script.c_str());
    return 1;
  }
  std::string line;
  int shots = 0;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == '#') continue;
    JsonDocument doc;
    if (deserializeJson(doc, line)) {
      fprintf(stderr, "bad line: %s\n", line.c_str());
      return 1;
    }
    const char *t = doc["t"] | "";
    if (!strcmp(t, "snap")) {
      pass_time(60);
      lv_refr_now(disp);
      const std::string path = out_dir + "/" + (doc["name"] | "screen") + ".bmp";
      if (!write_bmp(path)) {
        fprintf(stderr, "can't write %s\n", path.c_str());
        return 1;
      }
      fprintf(stderr, "[sim] wrote %s (%s)\n", path.c_str(), agent_ui::screen_name());
      shots++;
    } else if (!strcmp(t, "wait")) {
      pass_time(doc["ms"] | 0);
    } else if (!strcmp(t, "link")) {
      agent_ui::set_connected(doc["up"] | false);
    } else {
      agent_ui::handle_message(line.c_str(), line.size());
    }
  }
  fprintf(stderr, "[sim] %d pictures\n", shots);
  return 0;
}

// ---- window -----------------------------------------------------------------------------
int run_window(float zoom) {
  g_window = lv_sdl_window_create(agent_ui::SCREEN_W, agent_ui::SCREEN_H);
  lv_sdl_window_set_zoom(g_window, zoom);
  lv_sdl_window_set_title(g_window, "AI Agent Controller - LED: idle");

  // Keys go to one invisible object, which turns them into protocol inputs.
  lv_indev_t *kb = lv_sdl_keyboard_create();
  lv_group_t *group = lv_group_create();
  lv_obj_t *catcher = lv_obj_create(lv_layer_sys());
  lv_obj_remove_style_all(catcher);
  lv_obj_set_size(catcher, 0, 0);
  lv_group_add_obj(group, catcher);
  lv_indev_set_group(kb, group);
  lv_obj_add_event_cb(catcher, on_key, LV_EVENT_KEY, nullptr);

  agent_ui::Host host;
  host.send = host_send;
  host.led = host_led;
  host.sound = host_sound;
  agent_ui::begin(host);

  std::thread(stdin_reader).detach();

  const char *hello = "{\"v\":1,\"t\":\"hello\",\"device\":\"dock\",\"fw\":\"sim-0.1\",\"transports\":[\"usb\"],"
                      "\"screen\":{\"w\":480,\"h\":320}}";
  bool up = false;
  uint32_t last_rx = 0, last_ping = 0, last_hello = 0;
  bool said_hello = false;

  for (;;) {
    std::vector<std::string> lines;
    bool closed;
    {
      std::lock_guard<std::mutex> lock(g_in_mutex);
      lines.swap(g_in_lines);
      closed = g_stdin_closed;
    }
    const uint32_t now = real_ms();
    for (const std::string &l : lines) {
      last_rx = now;
      if (!up && l.find("\"welcome\"") != std::string::npos) up = true;
      agent_ui::handle_message(l.c_str(), l.size());
    }
    if (closed) return 0;  // the bridge went away

    // Link rules from protocol v1: ping every 500 ms; 2 s of silence means the link is down.
    if (up && now - last_rx > 2000) {
      up = false;
      agent_ui::set_connected(false);
    }
    if (up && now - last_ping >= 500) {
      last_ping = now;
      char buf[64];
      snprintf(buf, sizeof buf, "{\"v\":1,\"t\":\"ping\",\"ts\":%u}", now);
      send_line(buf);
    }
    if (!up && (!said_hello || now - last_hello >= 1000)) {  // keep knocking until the app answers
      said_hello = true;
      last_hello = now;
      send_line(hello);
    }

    const uint32_t wait = lv_timer_handler();
    usleep((wait > 10 ? 10 : wait) * 1000);
  }
}

}  // namespace

int main(int argc, char **argv) {
  std::string script, out_dir = ".";
  float zoom = 2.0f;
  for (int i = 1; i < argc; i++) {
    const std::string a = argv[i];
    if (a == "--script" && i + 1 < argc) script = argv[++i];
    else if (a == "--out" && i + 1 < argc) out_dir = argv[++i];
    else if (a == "--zoom" && i + 1 < argc) zoom = static_cast<float>(atof(argv[++i]));
    else {
      fprintf(stderr, "usage: agent-sim [--zoom 2] | agent-sim --script file.jsonl --out dir\n");
      return 2;
    }
  }
  lv_init();
  lv_tick_set_cb(tick_cb);
  return script.empty() ? run_window(zoom) : run_script(script, out_dir);
}
