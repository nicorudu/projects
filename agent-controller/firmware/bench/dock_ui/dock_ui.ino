// M4 bench step 3: the real screens (AgentUI + LVGL) on the dock's display.
// The screen code is the same library the desktop simulator runs (firmware/lib/AgentUI).
//
// Run dock_display first: it proves the wiring and tells you which settings below to keep.
// Wiring: firmware/bench/dock_display/README.md (blueprint section 5.1).
//
// Board: ESP32S3 Dev Module, Flash Size = 16MB, PSRAM = OPI PSRAM.
// Build: see README.md in this folder (it needs --library for AgentUI).
//
// What it shows: with no Mac attached it steps through demo screens every 4 seconds.
// It also takes protocol v1 JSON, one message per line, on the serial port at 115200 baud;
// the first line it receives stops the demo.
//
// State: compiles; not run on hardware yet. GPIO35-37 belong to the PSRAM; never use them.

#include <SPI.h>

#include <AgentUI.h>
#include <lvgl.h>

#include "demo_messages.h"

// ---- Pins (blueprint section 5.1) ---------------------------------------------------------
#define PIN_LCD_MOSI 11
#define PIN_LCD_SCLK 12
#define PIN_LCD_CS   10
#define PIN_LCD_DC    9
#define PIN_LCD_RST  14
#define PIN_LCD_BL    8

// ---- Copy these from what worked in dock_display -------------------------------------------
#define SPI_HZ          20000000UL
#define ROTATION        1   // 1 = landscape, 3 = landscape turned 180 degrees
#define COLOR_ORDER_BGR 1
#define INVERT_COLORS   1
#define BL_ACTIVE_HIGH  1

// ---- ST7796S ------------------------------------------------------------------------------
static void lcdCmd(uint8_t cmd, const uint8_t *data = nullptr, size_t n = 0) {
  SPI.beginTransaction(SPISettings(SPI_HZ, MSBFIRST, SPI_MODE0));
  digitalWrite(PIN_LCD_CS, LOW);
  digitalWrite(PIN_LCD_DC, LOW);
  SPI.write(cmd);
  digitalWrite(PIN_LCD_DC, HIGH);
  if (n) SPI.writeBytes(data, n);
  digitalWrite(PIN_LCD_CS, HIGH);
  SPI.endTransaction();
}

#define LCD_CMD(cmd, ...)                \
  do {                                   \
    const uint8_t d_[] = {__VA_ARGS__};  \
    lcdCmd(cmd, d_, sizeof(d_));         \
  } while (0)

static void lcdInit() {
  pinMode(PIN_LCD_CS, OUTPUT);
  digitalWrite(PIN_LCD_CS, HIGH);
  pinMode(PIN_LCD_DC, OUTPUT);
  pinMode(PIN_LCD_RST, OUTPUT);
  SPI.begin(PIN_LCD_SCLK, -1, PIN_LCD_MOSI, -1);

  digitalWrite(PIN_LCD_RST, HIGH); delay(10);
  digitalWrite(PIN_LCD_RST, LOW);  delay(20);
  digitalWrite(PIN_LCD_RST, HIGH); delay(150);

  lcdCmd(0x01); delay(150);
  lcdCmd(0x11); delay(150);
  LCD_CMD(0xF0, 0xC3);
  LCD_CMD(0xF0, 0x96);
  uint8_t mad = (ROTATION == 3) ? 0xE0 : 0x20;
  if (COLOR_ORDER_BGR) mad |= 0x08;
  LCD_CMD(0x36, mad);
  LCD_CMD(0x3A, 0x55);
  LCD_CMD(0xB4, 0x01);
  LCD_CMD(0xB6, 0x80, 0x02, 0x3B);
  LCD_CMD(0xE8, 0x40, 0x8A, 0x00, 0x00, 0x29, 0x19, 0xA5, 0x33);
  LCD_CMD(0xC1, 0x06);
  LCD_CMD(0xC2, 0xA7);
  LCD_CMD(0xC5, 0x18);
  delay(120);
  LCD_CMD(0xE0, 0xF0, 0x09, 0x0B, 0x06, 0x04, 0x15, 0x2F, 0x54, 0x42, 0x3C, 0x17, 0x14, 0x18, 0x1B);
  LCD_CMD(0xE1, 0xE0, 0x09, 0x0B, 0x06, 0x04, 0x03, 0x2B, 0x43, 0x42, 0x3B, 0x16, 0x14, 0x17, 0x1B);
  LCD_CMD(0xF0, 0x3C);
  LCD_CMD(0xF0, 0x69);
  delay(120);
  lcdCmd(INVERT_COLORS ? 0x21 : 0x20);
  lcdCmd(0x29);
  delay(20);
}

// ---- LVGL display driver --------------------------------------------------------------------
// LVGL draws 40 lines at a time into this buffer and hands each finished area to flushCb.
static const uint32_t DRAW_BUF_BYTES = agent_ui::SCREEN_W * 40 * 2;
static uint8_t drawBuf[DRAW_BUF_BYTES];

static void flushCb(lv_display_t *disp, const lv_area_t *a, uint8_t *px) {
  const uint32_t n = (uint32_t)lv_area_get_width(a) * (uint32_t)lv_area_get_height(a);
  lv_draw_sw_rgb565_swap(px, n);  // the panel wants the high byte first
  LCD_CMD(0x2A, (uint8_t)(a->x1 >> 8), (uint8_t)a->x1, (uint8_t)(a->x2 >> 8), (uint8_t)a->x2);
  LCD_CMD(0x2B, (uint8_t)(a->y1 >> 8), (uint8_t)a->y1, (uint8_t)(a->y2 >> 8), (uint8_t)a->y2);
  SPI.beginTransaction(SPISettings(SPI_HZ, MSBFIRST, SPI_MODE0));
  digitalWrite(PIN_LCD_CS, LOW);
  digitalWrite(PIN_LCD_DC, LOW);
  SPI.write(0x2C);
  digitalWrite(PIN_LCD_DC, HIGH);
  SPI.writeBytes(px, n * 2);
  digitalWrite(PIN_LCD_CS, HIGH);
  SPI.endTransaction();
  lv_display_flush_ready(disp);
}

static uint32_t tickCb() { return millis(); }

// ---- Host callbacks ---------------------------------------------------------------------------
static void hostSend(const char *json, void *) { Serial.println(json); }
static void hostLed(const char *mode, void *) { Serial.printf("# led %s\n", mode); }      // the WS2812B comes later
static void hostSound(const char *name, void *) { Serial.printf("# sound %s\n", name); }  // so does the speaker

// ---- Serial lines and the demo ------------------------------------------------------------------
static String line;
static bool demo = true;
static size_t demoStep = 0;
static uint32_t demoAt = 0;

void setup() {
  Serial.begin(115200);
  Serial.setRxBufferSize(8192);
  delay(300);
  Serial.println("# dock_ui: AgentUI on the dock display");

  ledcAttach(PIN_LCD_BL, 5000, 8);
  ledcWrite(PIN_LCD_BL, BL_ACTIVE_HIGH ? 0 : 255);
  lcdInit();

  lv_init();
  lv_tick_set_cb(tickCb);
  lv_display_t *disp = lv_display_create(agent_ui::SCREEN_W, agent_ui::SCREEN_H);
  lv_display_set_buffers(disp, drawBuf, nullptr, DRAW_BUF_BYTES, LV_DISPLAY_RENDER_MODE_PARTIAL);
  lv_display_set_flush_cb(disp, flushCb);

  agent_ui::Host host;
  host.send = hostSend;
  host.led = hostLed;
  host.sound = hostSound;
  agent_ui::begin(host);
  lv_timer_handler();
  ledcWrite(PIN_LCD_BL, BL_ACTIVE_HIGH ? 255 : 0);  // light up once the first frame is drawn
}

void loop() {
  while (Serial.available()) {
    const char c = (char)Serial.read();
    if (c == '\n') {
      if (line.length()) {
        demo = false;
        agent_ui::handle_message(line.c_str(), line.length());
      }
      line = "";
    } else if (c != '\r' && line.length() < 8000) {
      line += c;
    }
  }

  if (demo && millis() - demoAt >= (demoStep ? 4000 : 1500)) {
    demoAt = millis();
    const char *m = DEMO_MESSAGES[demoStep % DEMO_COUNT];
    agent_ui::handle_message(m, strlen(m));
    demoStep++;
  }

  lv_timer_handler();
  delay(5);
}
