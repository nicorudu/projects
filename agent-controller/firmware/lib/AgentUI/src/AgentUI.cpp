// AgentUI: draws the screens from protocol v1 messages. See AgentUI.h.
//
// How it works: the last `view` (plus any `patch`es) is kept as a JSON document. Each change
// calls render(), which builds the screen's objects once and afterwards only touches what
// changed, so the display redraws small areas instead of the whole screen.

#include "AgentUI.h"

#include <string.h>

#include <string>
#include <vector>

#include <ArduinoJson.h>

#include "ui_text.h"
#include "ui_theme.h"

namespace agent_ui {
namespace {

namespace th = theme;

// ---- state ----------------------------------------------------------------------------
Host g_host;
bool g_started = false;
bool g_connected = false;
JsonDocument g_view;             // the screen as the Mac last described it
std::string g_screen;            // which screen's objects exist now
int64_t g_clock_offset_ms = 0;   // Mac clock minus LVGL's tick, set by "welcome"

lv_obj_t *g_root = nullptr;
lv_obj_t *g_toast = nullptr, *g_toast_label = nullptr;
lv_obj_t *g_banner = nullptr;
lv_timer_t *g_toast_timer = nullptr;

int64_t now_s() { return (g_clock_offset_ms + static_cast<int64_t>(lv_tick_get())) / 1000; }

// ---- small helpers ----------------------------------------------------------------------
lv_color_t col(uint32_t hex) { return lv_color_hex(hex); }

uint32_t status_color(const char *status) {
  if (!strcmp(status, "working")) return th::WORKING;
  if (!strcmp(status, "waiting")) return th::WAITING;
  if (!strcmp(status, "done")) return th::DONE;
  if (!strcmp(status, "error")) return th::ERROR_C;
  if (!strcmp(status, "ready")) return th::READY;
  return th::IDLE;
}

// A plain rectangle with none of the theme's padding, border or scrolling.
lv_obj_t *make_box(lv_obj_t *parent, int x, int y, int w, int h) {
  lv_obj_t *o = lv_obj_create(parent);
  lv_obj_remove_style_all(o);
  lv_obj_set_pos(o, x, y);
  lv_obj_set_size(o, w, h);
  lv_obj_set_scrollable(o, false);
  return o;
}

void fill(lv_obj_t *o, uint32_t color, int radius = 0) {
  lv_obj_set_style_bg_color(o, col(color), 0);
  lv_obj_set_style_bg_opa(o, LV_OPA_COVER, 0);
  lv_obj_set_style_radius(o, radius, 0);
}

// w = 0: as wide as the text. w > 0: one line of that width, cut short with dots.
lv_obj_t *make_label(lv_obj_t *parent, const lv_font_t *font, uint32_t color, int x, int y, int w = 0) {
  lv_obj_t *l = lv_label_create(parent);
  lv_obj_set_style_text_font(l, font, 0);
  lv_obj_set_style_text_color(l, col(color), 0);
  lv_obj_set_pos(l, x, y);
  if (w > 0) {
    lv_label_set_long_mode(l, LV_LABEL_LONG_MODE_DOTS);
    lv_obj_set_size(l, w, lv_font_get_line_height(font));
  }
  lv_label_set_text(l, "");
  return l;
}

// Only touch the label when the text really changed, so nothing is redrawn for no reason.
void set_text(lv_obj_t *label, const std::string &s) {
  if (strcmp(lv_label_get_text(label), s.c_str()) != 0) lv_label_set_text(label, s.c_str());
}

void set_hidden(lv_obj_t *o, bool hidden) {
  if (lv_obj_is_hidden(o) != hidden) lv_obj_set_hidden(o, hidden);
}

void style_scrollbar(lv_obj_t *o) {
  lv_obj_set_style_bg_color(o, col(th::TEXT_DIM), LV_PART_SCROLLBAR);
  lv_obj_set_style_bg_opa(o, LV_OPA_70, LV_PART_SCROLLBAR);
  lv_obj_set_style_width(o, 4, LV_PART_SCROLLBAR);
  lv_obj_set_style_radius(o, 2, LV_PART_SCROLLBAR);
  lv_obj_set_style_pad_right(o, 2, LV_PART_SCROLLBAR);
}

// ---- Agents (home) ----------------------------------------------------------------------
struct RowW {
  lv_obj_t *box, *dot, *status, *tool, *age, *title;
  std::string status_s;
  uint32_t outline = 0xFFFFFFFF;  // last outline color set (never a real color at first)
};
struct {
  lv_obj_t *counts, *list, *empty;
  std::vector<RowW> rows;
  int sel = -1;
} home;

void build_home() {
  home.rows.clear();
  home.sel = -1;
  lv_obj_t *title = make_label(g_root, th::font_small(), th::TEXT_DIM, 14, 12);
  lv_obj_set_style_text_letter_space(title, 2, 0);
  lv_label_set_text(title, "AGENTS");
  home.counts = make_label(g_root, th::font_small(), th::TEXT_DIM, 0, 0);
  lv_obj_align(home.counts, LV_ALIGN_TOP_RIGHT, -14, 12);

  home.list = make_box(g_root, 0, th::HEADER_H, SCREEN_W, SCREEN_H - th::HEADER_H);
  lv_obj_set_scrollable(home.list, true);
  lv_obj_set_scroll_dir(home.list, LV_DIR_VER);
  lv_obj_set_scrollbar_mode(home.list, LV_SCROLLBAR_MODE_OFF);
  lv_obj_set_style_pad_bottom(home.list, th::MARGIN, 0);

  home.empty = make_label(g_root, th::font_body(), th::TEXT_DIM, 0, 0);
  lv_obj_set_style_text_align(home.empty, LV_TEXT_ALIGN_CENTER, 0);
  lv_label_set_text(home.empty, "No sessions yet\nStart Claude Code in a terminal");
  lv_obj_align(home.empty, LV_ALIGN_CENTER, 0, 10);
}

RowW make_row(int index) {
  RowW r;
  r.box = make_box(home.list, th::MARGIN, 2 + index * (th::ROW_H + th::ROW_GAP), SCREEN_W - 2 * th::MARGIN, th::ROW_H);
  fill(r.box, th::PANEL, th::RADIUS);
  lv_obj_set_style_border_width(r.box, th::OUTLINE, 0);
  lv_obj_set_style_border_opa(r.box, LV_OPA_COVER, 0);
  r.dot = make_box(r.box, 12, 12, 10, 10);
  fill(r.dot, th::IDLE, LV_RADIUS_CIRCLE);
  r.status = make_label(r.box, th::font_label(), th::IDLE, 30, 8);
  r.tool = make_label(r.box, th::font_small(), th::TEXT_DIM, 128, 10, 262);
  r.age = make_label(r.box, th::font_small(), th::TEXT_DIM, 0, 0);
  lv_obj_align(r.age, LV_ALIGN_TOP_RIGHT, -12, 10);
  r.title = make_label(r.box, th::font_title(), th::TEXT, 12, 29, 436);
  return r;
}

void update_home() {
  JsonArray rows = g_view["rows"].as<JsonArray>();
  const size_t n = rows.size();
  const bool count_changed = home.rows.size() != n;
  while (home.rows.size() > n) {
    lv_obj_delete(home.rows.back().box);
    home.rows.pop_back();
  }
  while (home.rows.size() < n) home.rows.push_back(make_row(static_cast<int>(home.rows.size())));

  int sel = g_view["sel"] | 0;
  if (sel >= static_cast<int>(n)) sel = static_cast<int>(n) - 1;
  const int64_t now = now_s();

  for (size_t i = 0; i < n; i++) {
    JsonObject row = rows[i];
    RowW &w = home.rows[i];
    const char *status = row["status"] | "idle";
    const uint32_t color = status_color(status);
    if (w.status_s != status) {
      w.status_s = status;
      lv_obj_set_style_bg_color(w.dot, col(color), 0);
      lv_obj_set_style_text_color(w.status, col(color), 0);
      set_text(w.status, upper(status));
    }
    const uint32_t outline = static_cast<int>(i) == sel ? color : th::PANEL;
    if (w.outline != outline) {
      w.outline = outline;
      lv_obj_set_style_border_color(w.box, col(outline), 0);
    }
    // Large text: the task title. Small text: the project (when the title is a task) and the tool.
    const char *name = row["name"] | "";
    const char *title = row["title"] | name;
    std::string small = strcmp(title, name) != 0 ? clean_text(name, false) : std::string();
    const std::string tool = clean_text(row["tool"] | "", false);
    if (!small.empty() && !tool.empty()) small += "  \xE2\x80\xA2  ";
    small += tool;
    set_text(w.title, clean_text(title, false));
    set_text(w.tool, small);
    set_text(w.age, age(now - (row["since"] | now)));
  }

  if (n > 0 && (sel != home.sel || count_changed)) {
    lv_obj_update_layout(home.list);
    lv_obj_scroll_to_view(home.rows[sel].box, LV_ANIM_OFF);
  }
  home.sel = sel;
  set_hidden(home.empty, n > 0);

  JsonObject header = g_view["header"];
  const int waiting = header["waiting"] | 0, working = header["working"] | 0;
  std::string counts;
  if (waiting) counts += std::to_string(waiting) + " waiting";
  if (waiting && working) counts += "  \xE2\x80\xA2  ";
  if (working) counts += std::to_string(working) + " working";
  set_text(home.counts, counts);
  lv_obj_align(home.counts, LV_ALIGN_TOP_RIGHT, -14, 12);
}

// ---- Detail -----------------------------------------------------------------------------
struct {
  lv_obj_t *dot, *name, *status, *worked, *scroll, *text;
  std::string status_s, id;
  int reported_max = -1;
} detail;

void build_detail() {
  detail.status_s.clear();
  detail.id.clear();
  detail.reported_max = -1;
  detail.dot = make_box(g_root, 14, 17, 12, 12);
  fill(detail.dot, th::IDLE, LV_RADIUS_CIRCLE);
  detail.name = make_label(g_root, th::font_title(), th::TEXT, 36, 10, 320);
  detail.status = make_label(g_root, th::font_label(), th::IDLE, 0, 0);
  detail.worked = make_label(g_root, th::font_label(), th::TEXT_DIM, 14, 42, SCREEN_W - 28);

  detail.scroll = make_box(g_root, 0, 70, SCREEN_W, SCREEN_H - 70 - th::MARGIN);
  lv_obj_set_scrollable(detail.scroll, true);
  lv_obj_set_scroll_dir(detail.scroll, LV_DIR_VER);
  lv_obj_set_scrollbar_mode(detail.scroll, LV_SCROLLBAR_MODE_AUTO);
  style_scrollbar(detail.scroll);

  detail.text = lv_label_create(detail.scroll);
  lv_obj_set_style_text_font(detail.text, th::font_body(), 0);
  lv_obj_set_style_text_line_space(detail.text, 4, 0);
  lv_label_set_long_mode(detail.text, LV_LABEL_LONG_MODE_WRAP);
  lv_obj_set_pos(detail.text, 14, 0);
  lv_obj_set_width(detail.text, SCREEN_W - 14 - 18);  // room for the scrollbar on the right
  lv_label_set_text(detail.text, "");
}

void update_detail() {
  const char *status = g_view["status"] | "idle";
  const uint32_t color = status_color(status);
  if (detail.status_s != status) {
    detail.status_s = status;
    lv_obj_set_style_bg_color(detail.dot, col(color), 0);
    lv_obj_set_style_text_color(detail.status, col(color), 0);
    set_text(detail.status, upper(status));
    lv_obj_align(detail.status, LV_ALIGN_TOP_RIGHT, -14, 14);
  }
  const char *name = g_view["name"] | "";
  const char *title = g_view["title"] | name;
  set_text(detail.name, clean_text(title, false));

  const int64_t now = now_s();
  std::string line;
  if (!g_view["turn_start"].isNull()) line = "Working for " + duration(now - g_view["turn_start"].as<int64_t>());
  else if (!g_view["worked_s"].isNull()) line = "Worked for " + duration(g_view["worked_s"].as<int64_t>());
  else line = age(now - (g_view["since"] | now)) + " ago";
  if (strcmp(title, name) != 0) line += "  \xE2\x80\xA2  " + clean_text(name, false);  // which project
  const std::string tool = clean_text(g_view["tool"] | "", false);
  if (!tool.empty()) line += "  \xE2\x80\xA2  " + tool;
  set_text(detail.worked, line);

  const std::string text = clean_text(g_view["text"] | "", true);
  const bool has_text = !text.empty();
  lv_obj_set_style_text_color(detail.text, col(has_text ? th::TEXT_SOFT : th::TEXT_DIM), 0);
  set_text(detail.text, has_text ? text : std::string("No messages yet."));

  // How far can it scroll? Tell the Mac, so stick-down stops at the end instead of counting on.
  lv_obj_update_layout(detail.scroll);
  const int max_px = lv_obj_get_scroll_y(detail.scroll) + lv_obj_get_scroll_bottom(detail.scroll);
  const int max_steps = max_px <= 0 ? 0 : (max_px + th::SCROLL_STEP - 1) / th::SCROLL_STEP;
  int y = (g_view["scroll"] | 0) * th::SCROLL_STEP;
  if (y > max_px) y = max_px;
  if (y < 0) y = 0;
  if (lv_obj_get_scroll_y(detail.scroll) != y) lv_obj_scroll_to_y(detail.scroll, y, LV_ANIM_OFF);

  const char *id = g_view["id"] | "";
  if (g_host.send && (max_steps != detail.reported_max || detail.id != id)) {
    detail.reported_max = max_steps;
    detail.id = id;
    JsonDocument m;
    m["v"] = 1;
    m["t"] = "layout";
    m["screen"] = "detail";
    m["id"] = id;
    m["max_scroll"] = max_steps;
    std::string out;
    serializeJson(m, out);
    g_host.send(out.c_str(), g_host.ctx);
  }
}

// ---- Approval ---------------------------------------------------------------------------
struct OptionW {
  lv_obj_t *box, *label;
};
struct {
  lv_obj_t *queue, *title, *summary;
  std::vector<OptionW> options;
  int sel = -1;
} approval;

constexpr int OPTION_H = 32, OPTION_GAP = 4, OPTIONS_Y = 148;

void build_approval() {
  approval.options.clear();
  approval.sel = -1;
  lv_obj_t *bar = make_box(g_root, 0, 0, SCREEN_W, 3);
  fill(bar, th::WAITING);
  lv_obj_t *head = make_label(g_root, th::font_small(), th::WAITING, 14, 12);
  lv_obj_set_style_text_letter_space(head, 2, 0);
  lv_label_set_text(head, "APPROVAL");
  approval.queue = make_label(g_root, th::font_small(), th::TEXT_DIM, 0, 0);
  approval.title = make_label(g_root, th::font_body(), th::TEXT, 14, 36, SCREEN_W - 28);

  lv_obj_t *panel = make_box(g_root, th::MARGIN, 64, SCREEN_W - 2 * th::MARGIN, 78);
  fill(panel, th::PANEL, th::RADIUS);
  approval.summary = lv_label_create(panel);
  lv_obj_set_style_text_font(approval.summary, th::font_label(), 0);
  lv_obj_set_style_text_color(approval.summary, col(th::TEXT_SOFT), 0);
  lv_label_set_long_mode(approval.summary, LV_LABEL_LONG_MODE_DOTS);
  lv_obj_set_pos(approval.summary, 10, 8);
  lv_obj_set_size(approval.summary, SCREEN_W - 2 * th::MARGIN - 20, 62);
  lv_label_set_text(approval.summary, "");

  lv_obj_t *hint = make_label(g_root, th::font_small(), th::TEXT_DIM, 14, 0);
  lv_label_set_text(hint, "Send confirms  \xE2\x80\xA2  Cancel rejects");
  lv_obj_align(hint, LV_ALIGN_BOTTOM_LEFT, 14, -8);
}

void update_approval() {
  const std::string who = clean_text(g_view["session"] | "", false);
  const std::string tool = clean_text(g_view["tool"] | "", false);
  set_text(approval.title, who + " wants to use " + tool);
  set_text(approval.summary, clean_text(g_view["summary"] | "", true));
  const int queue = g_view["queue"] | 1;
  set_text(approval.queue, queue > 1 ? std::to_string(queue) + " waiting" : std::string());
  lv_obj_align(approval.queue, LV_ALIGN_TOP_RIGHT, -14, 12);

  JsonArray options = g_view["options"].as<JsonArray>();
  const size_t n = options.size();
  while (approval.options.size() > n) {
    lv_obj_delete(approval.options.back().box);
    approval.options.pop_back();
    approval.sel = -1;
  }
  while (approval.options.size() < n) {
    const int i = static_cast<int>(approval.options.size());
    OptionW o;
    o.box = make_box(g_root, th::MARGIN, OPTIONS_Y + i * (OPTION_H + OPTION_GAP), SCREEN_W - 2 * th::MARGIN, OPTION_H);
    fill(o.box, th::PANEL, th::RADIUS);
    lv_obj_set_style_border_width(o.box, th::OUTLINE, 0);
    lv_obj_set_style_border_color(o.box, col(th::PANEL), 0);
    o.label = make_label(o.box, th::font_label(), th::TEXT_SOFT, 12, 5, SCREEN_W - 2 * th::MARGIN - 30);
    approval.options.push_back(o);
    approval.sel = -1;
  }
  for (size_t i = 0; i < n; i++) set_text(approval.options[i].label, clean_text(options[i] | "", false));

  const int sel = g_view["sel"] | 0;
  if (sel != approval.sel) {
    for (size_t i = 0; i < n; i++) {
      const bool on = static_cast<int>(i) == sel;
      OptionW &o = approval.options[i];
      lv_obj_set_style_border_color(o.box, col(on ? th::WAITING : th::PANEL), 0);
      lv_obj_set_style_bg_color(o.box, col(on ? th::PANEL_HI : th::PANEL), 0);
      lv_obj_set_style_text_color(o.label, col(on ? th::TEXT : th::TEXT_SOFT), 0);
    }
    approval.sel = sel;
  }
}

// ---- Voice (M2; the layout is ready, the engine is not) ----------------------------------
struct {
  lv_obj_t *bar, *state, *bubble, *text;
  std::string state_s;
} voice;

void bar_opa_cb(void *obj, int32_t v) {
  lv_obj_set_style_bg_opa(static_cast<lv_obj_t *>(obj), static_cast<lv_opa_t>(v), 0);
}

void build_voice() {
  voice.state_s = "?";
  voice.bar = make_box(g_root, 0, 0, SCREEN_W, 6);
  fill(voice.bar, th::RECORDING);
  lv_obj_set_style_shadow_color(voice.bar, col(th::WORKING), 0);
  lv_obj_set_style_shadow_width(voice.bar, 24, 0);
  lv_obj_set_style_shadow_opa(voice.bar, LV_OPA_70, 0);
  voice.state = make_label(g_root, th::font_title(), th::TEXT, 0, 0);
  voice.bubble = make_box(g_root, th::MARGIN, 170, SCREEN_W - 2 * th::MARGIN, 140);
  fill(voice.bubble, th::PANEL, 14);
  voice.text = lv_label_create(voice.bubble);
  lv_obj_set_style_text_font(voice.text, th::font_body(), 0);
  lv_obj_set_style_text_color(voice.text, col(th::TEXT_SOFT), 0);
  lv_obj_set_style_text_line_space(voice.text, 4, 0);
  lv_label_set_long_mode(voice.text, LV_LABEL_LONG_MODE_DOTS);
  lv_obj_set_pos(voice.text, 14, 12);
  lv_obj_set_size(voice.text, SCREEN_W - 2 * th::MARGIN - 28, 116);
  lv_label_set_text(voice.text, "");
}

void update_voice() {
  const char *state = g_view["state"] | "idle";
  if (voice.state_s != state) {
    voice.state_s = state;
    const bool recording = !strcmp(state, "recording");
    const char *words = "Hold Voice to talk";
    if (recording) words = "Listening...";
    else if (!strcmp(state, "transcribing")) words = "Transcribing...";
    else if (!strcmp(state, "review")) words = "Send delivers  \xE2\x80\xA2  Cancel discards";
    else if (!strcmp(state, "sending")) words = "Sending...";
    lv_label_set_text(voice.state, words);
    lv_obj_align(voice.state, LV_ALIGN_TOP_MID, 0, 80);
    lv_anim_delete(voice.bar, bar_opa_cb);
    set_hidden(voice.bar, !recording);
    if (recording) {  // the bar along the top breathes while the mics are open
      lv_anim_t a;
      lv_anim_init(&a);
      lv_anim_set_var(&a, voice.bar);
      lv_anim_set_exec_cb(&a, bar_opa_cb);
      lv_anim_set_values(&a, LV_OPA_COVER, LV_OPA_40);
      lv_anim_set_duration(&a, 700);
      lv_anim_set_reverse_duration(&a, 700);
      lv_anim_set_repeat_count(&a, LV_ANIM_REPEAT_INFINITE);
      lv_anim_start(&a);
    }
  }
  const std::string text = clean_text(g_view["text"] | "", true);
  set_text(voice.text, text);
  set_hidden(voice.bubble, text.empty());
}

// ---- Connecting -------------------------------------------------------------------------
void build_connecting() {
  lv_obj_t *a = make_label(g_root, th::font_title(), th::TEXT, 0, 0);
  lv_label_set_text(a, "Connecting...");
  lv_obj_align(a, LV_ALIGN_CENTER, 0, -14);
  lv_obj_t *b = make_label(g_root, th::font_small(), th::TEXT_DIM, 0, 0);
  lv_label_set_text(b, "Waiting for the companion app");
  lv_obj_align(b, LV_ALIGN_CENTER, 0, 16);
}

// ---- render -----------------------------------------------------------------------------
void render() {
  if (!g_started) return;
  const char *want = g_view["screen"] | "connecting";
  const bool known = !strcmp(want, "home") || !strcmp(want, "detail") || !strcmp(want, "approval") ||
                     !strcmp(want, "voice");
  if (!known) want = "connecting";

  if (g_screen != want) {
    lv_anim_delete(voice.bar, bar_opa_cb);  // its object is about to go
    voice.bar = nullptr;
    lv_obj_clean(g_root);
    g_screen = want;
    if (g_screen == "home") build_home();
    else if (g_screen == "detail") build_detail();
    else if (g_screen == "approval") build_approval();
    else if (g_screen == "voice") build_voice();
    else build_connecting();
  }
  if (g_screen == "home") update_home();
  else if (g_screen == "detail") update_detail();
  else if (g_screen == "approval") update_approval();
  else if (g_screen == "voice") update_voice();

  set_hidden(g_banner, g_connected || g_screen == "connecting");
}

void second_tick(lv_timer_t *) { render(); }  // keeps "2m" and "Working for ..." counting

// ---- toast and banner (drawn above every screen) ------------------------------------------
lv_obj_t *make_pill(uint32_t bg, const lv_font_t *font, lv_obj_t **label_out) {
  lv_obj_t *pill = lv_obj_create(lv_layer_top());
  lv_obj_remove_style_all(pill);
  lv_obj_set_scrollable(pill, false);
  lv_obj_set_size(pill, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
  fill(pill, bg, 16);
  lv_obj_set_style_pad_hor(pill, 16, 0);
  lv_obj_set_style_pad_ver(pill, 8, 0);
  lv_obj_t *l = lv_label_create(pill);
  lv_obj_set_style_text_font(l, font, 0);
  lv_obj_set_style_text_color(l, col(th::TEXT), 0);
  lv_label_set_text(l, "");
  if (label_out) *label_out = l;
  return pill;
}

void toast_done(lv_timer_t *) {
  g_toast_timer = nullptr;  // a one-shot timer deletes itself
  set_hidden(g_toast, true);
}

void show_toast(const char *text, uint32_t ms) {
  lv_label_set_text(g_toast_label, clean_text(text, false).c_str());
  set_hidden(g_toast, false);
  lv_obj_align(g_toast, LV_ALIGN_BOTTOM_MID, 0, -14);
  if (g_toast_timer) lv_timer_delete(g_toast_timer);
  g_toast_timer = lv_timer_create(toast_done, ms ? ms : 1500, nullptr);
  lv_timer_set_repeat_count(g_toast_timer, 1);
}

// Copy `src` into the kept view. Rebuilding the document each time keeps its memory compact.
void store_view(JsonObjectConst src, bool merge) {
  JsonDocument next;
  JsonObject dst = next.to<JsonObject>();
  if (merge) {
    for (JsonPairConst kv : g_view.as<JsonObjectConst>()) dst[kv.key()] = kv.value();
  }
  for (JsonPairConst kv : src) {
    if (kv.key() == "v" || kv.key() == "t") continue;
    dst[kv.key()] = kv.value();
  }
  g_view = std::move(next);
}

}  // namespace

// ---- public -----------------------------------------------------------------------------
void begin(const Host &host) {
  g_host = host;
  g_view.clear();
  g_screen.clear();
  g_connected = false;

  lv_obj_t *scr = lv_screen_active();
  lv_obj_remove_style_all(scr);
  fill(scr, th::BG);
  lv_obj_set_scrollable(scr, false);
  g_root = make_box(scr, 0, 0, SCREEN_W, SCREEN_H);

  g_toast = make_pill(0x2A2F38, th::font_label(), &g_toast_label);
  set_hidden(g_toast, true);
  lv_obj_t *banner_label = nullptr;
  g_banner = make_pill(th::ERROR_C, th::font_small(), &banner_label);
  lv_label_set_text(banner_label, "Disconnected");
  lv_obj_set_style_text_color(banner_label, col(0x1A0507), 0);
  lv_obj_set_style_pad_ver(g_banner, 4, 0);
  lv_obj_align(g_banner, LV_ALIGN_TOP_MID, 0, 6);
  set_hidden(g_banner, true);

  lv_timer_create(second_tick, 1000, nullptr);
  g_started = true;
  render();
}

void handle_message(const char *json, size_t len) {
  if (!g_started || !json || !len) return;
  JsonDocument doc;
  if (deserializeJson(doc, json, len)) return;  // not JSON
  if (!doc.is<JsonObject>() || (doc["v"] | 0) != 1) return;
  const char *t = doc["t"] | "";

  if (!strcmp(t, "welcome")) {
    if (doc["mac_ms"].is<int64_t>()) g_clock_offset_ms = doc["mac_ms"].as<int64_t>() - static_cast<int64_t>(lv_tick_get());
    g_connected = true;
    if (doc["view"].is<JsonObjectConst>()) store_view(doc["view"].as<JsonObjectConst>(), false);
    else g_view.clear();
    render();
  } else if (!strcmp(t, "view")) {
    store_view(doc.as<JsonObjectConst>(), false);
    render();
  } else if (!strcmp(t, "patch")) {
    const char *screen = doc["screen"] | "";
    const char *showing = g_view["screen"] | "";
    if (strcmp(screen, showing) != 0 || !doc["set"].is<JsonObjectConst>()) return;  // not for this screen
    store_view(doc["set"].as<JsonObjectConst>(), true);
    render();
  } else if (!strcmp(t, "toast")) {
    show_toast(doc["text"] | "", doc["ms"] | 1500);
  } else if (!strcmp(t, "led")) {
    if (g_host.led) g_host.led(doc["mode"] | "idle", g_host.ctx);
  } else if (!strcmp(t, "sound")) {
    if (g_host.sound) g_host.sound(doc["name"] | "alert", g_host.ctx);
  }
  // pong and ack belong to the link layer, not the screens.
}

void set_connected(bool connected) {
  if (g_connected == connected) return;
  g_connected = connected;
  render();
}

const char *screen_name() { return g_screen.c_str(); }

}  // namespace agent_ui
