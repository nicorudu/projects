// M4 bench step 2: display + touch test for the dock.
// Module: LCDWIKI MSP4031, 4.0" 320x480, ST7796S (SPI) + FT6336U touch (I2C).
// Wiring and pass conditions: see README.md in this folder. Pins follow blueprint §5.1.
//
// Board: ESP32S3 Dev Module, Flash Size = 16MB, PSRAM = OPI PSRAM.
// Build: arduino-cli compile -b esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi
// Serial: 115200 baud on the UART/COM port.
//
// No libraries beyond the ESP32 core (SPI, Wire). This is a bench check only;
// the real dock firmware draws with LVGL.
// GPIO35-37 belong to the octal PSRAM; never use them.

#include <SPI.h>
#include <Wire.h>

// ---- Pins (blueprint §5.1) -------------------------------------------------
#define PIN_LCD_MOSI 11
#define PIN_LCD_SCLK 12
#define PIN_LCD_CS   10
#define PIN_LCD_DC    9   // module pin "LCD_RS"
#define PIN_LCD_RST  14
#define PIN_LCD_BL    8   // module pin "LED", PWM dimming
#define PIN_TP_SDA    1
#define PIN_TP_SCL    2
#define PIN_TP_INT    4
#define PIN_TP_RST    5   // not in the blueprint before this test; taken from the free pins

// ---- Things to flip if the picture or touch is wrong -----------------------
#define SPI_HZ          20000000UL  // 20 MHz is safe on 20 cm jumpers; 40 MHz later
#define ROTATION        1           // 1 = landscape, 3 = landscape turned 180 degrees
#define COLOR_ORDER_BGR 1           // set to 0 if red and blue are swapped
#define INVERT_COLORS   1           // set to 0 if colors look like a photo negative
#define BL_ACTIVE_HIGH  1           // set to 0 if the screen is dark at full brightness
#define TOUCH_SWAP_XY   1           // touch reports portrait; the screen is landscape
#define TOUCH_FLIP_X    0
#define TOUCH_FLIP_Y    1

#define SCREEN_W 480
#define SCREEN_H 320
#define TP_ADDR  0x38

// ---- Colors (RGB565) --------------------------------------------------------
static constexpr uint16_t rgb(uint8_t r, uint8_t g, uint8_t b) {
  return (uint16_t)(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3));
}
const uint16_t BLACK = rgb(0, 0, 0), WHITE = rgb(255, 255, 255);
const uint16_t RED = rgb(255, 0, 0), GREEN = rgb(0, 255, 0), BLUE = rgb(0, 0, 255);
const uint16_t YELLOW = rgb(255, 255, 0), CYAN = rgb(0, 255, 255), MAGENTA = rgb(255, 0, 255);

// ---- ST7796S ------------------------------------------------------------------
static uint8_t lineBuf[SCREEN_W * 2];

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

#define LCD_CMD(cmd, ...)                       \
  do {                                          \
    const uint8_t d_[] = {__VA_ARGS__};         \
    lcdCmd(cmd, d_, sizeof(d_));                \
  } while (0)

static void lcdInit() {
  pinMode(PIN_LCD_CS, OUTPUT);
  digitalWrite(PIN_LCD_CS, HIGH);
  pinMode(PIN_LCD_DC, OUTPUT);
  pinMode(PIN_LCD_RST, OUTPUT);
  SPI.begin(PIN_LCD_SCLK, -1, PIN_LCD_MOSI, -1);  // MISO is not wired

  digitalWrite(PIN_LCD_RST, HIGH); delay(10);
  digitalWrite(PIN_LCD_RST, LOW);  delay(20);
  digitalWrite(PIN_LCD_RST, HIGH); delay(150);

  lcdCmd(0x01); delay(150);                     // software reset
  lcdCmd(0x11); delay(150);                     // sleep out
  LCD_CMD(0xF0, 0xC3);                          // unlock the extended commands
  LCD_CMD(0xF0, 0x96);
  uint8_t mad = (ROTATION == 3) ? 0xE0 : 0x20;  // MV (+ MX, MY) = landscape
  if (COLOR_ORDER_BGR) mad |= 0x08;
  LCD_CMD(0x36, mad);                           // memory access control
  LCD_CMD(0x3A, 0x55);                          // 16 bits per pixel
  LCD_CMD(0xB4, 0x01);                          // 1-dot inversion
  LCD_CMD(0xB6, 0x80, 0x02, 0x3B);              // display function control
  LCD_CMD(0xE8, 0x40, 0x8A, 0x00, 0x00, 0x29, 0x19, 0xA5, 0x33);
  LCD_CMD(0xC1, 0x06);                          // power control 2
  LCD_CMD(0xC2, 0xA7);                          // power control 3
  LCD_CMD(0xC5, 0x18);                          // VCOM
  delay(120);
  LCD_CMD(0xE0, 0xF0, 0x09, 0x0B, 0x06, 0x04, 0x15, 0x2F, 0x54, 0x42, 0x3C, 0x17, 0x14, 0x18, 0x1B);
  LCD_CMD(0xE1, 0xE0, 0x09, 0x0B, 0x06, 0x04, 0x03, 0x2B, 0x43, 0x42, 0x3B, 0x16, 0x14, 0x17, 0x1B);
  LCD_CMD(0xF0, 0x3C);                          // lock the extended commands
  LCD_CMD(0xF0, 0x69);
  delay(120);
  lcdCmd(INVERT_COLORS ? 0x21 : 0x20);          // inversion on / off
  lcdCmd(0x29);                                 // display on
  delay(20);
}

static void fillRect(int x, int y, int w, int h, uint16_t color) {
  if (x < 0) { w += x; x = 0; }
  if (y < 0) { h += y; y = 0; }
  if (x + w > SCREEN_W) w = SCREEN_W - x;
  if (y + h > SCREEN_H) h = SCREEN_H - y;
  if (w <= 0 || h <= 0) return;

  const int x1 = x + w - 1, y1 = y + h - 1;
  LCD_CMD(0x2A, (uint8_t)(x >> 8), (uint8_t)x, (uint8_t)(x1 >> 8), (uint8_t)x1);
  LCD_CMD(0x2B, (uint8_t)(y >> 8), (uint8_t)y, (uint8_t)(y1 >> 8), (uint8_t)y1);

  for (int i = 0; i < w; i++) {
    lineBuf[2 * i] = (uint8_t)(color >> 8);
    lineBuf[2 * i + 1] = (uint8_t)color;
  }
  SPI.beginTransaction(SPISettings(SPI_HZ, MSBFIRST, SPI_MODE0));
  digitalWrite(PIN_LCD_CS, LOW);
  digitalWrite(PIN_LCD_DC, LOW);
  SPI.write(0x2C);                              // memory write
  digitalWrite(PIN_LCD_DC, HIGH);
  for (int row = 0; row < h; row++) SPI.writeBytes(lineBuf, (uint32_t)w * 2);
  digitalWrite(PIN_LCD_CS, HIGH);
  SPI.endTransaction();
}

static void frame(uint16_t color, int t) {      // outline t pixels thick at the screen edge
  fillRect(0, 0, SCREEN_W, t, color);
  fillRect(0, SCREEN_H - t, SCREEN_W, t, color);
  fillRect(0, 0, t, SCREEN_H, color);
  fillRect(SCREEN_W - t, 0, t, SCREEN_H, color);
}

static void backlight(uint8_t level) {          // 0 = off, 255 = full
  ledcWrite(PIN_LCD_BL, BL_ACTIVE_HIGH ? level : 255 - level);
}

// ---- FT6336U ------------------------------------------------------------------
static volatile uint32_t tpIntCount = 0;
static void IRAM_ATTR onTouchInt() { tpIntCount = tpIntCount + 1; }

static bool tpRead(uint8_t reg, uint8_t *buf, size_t n) {
  Wire.beginTransmission(TP_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((uint8_t)TP_ADDR, (uint8_t)n) != n) return false;
  for (size_t i = 0; i < n; i++) buf[i] = Wire.read();
  return true;
}

static bool tpFound = false;

static void touchInit() {
  pinMode(PIN_TP_INT, INPUT_PULLUP);
  pinMode(PIN_TP_RST, OUTPUT);
  digitalWrite(PIN_TP_RST, LOW);  delay(20);
  digitalWrite(PIN_TP_RST, HIGH); delay(300);
  Wire.begin(PIN_TP_SDA, PIN_TP_SCL, 400000);

  Serial.print("i2c scan:   ");
  int found = 0;
  for (uint8_t a = 0x08; a < 0x78; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.printf("0x%02X ", a);
      found++;
      if (a == TP_ADDR) tpFound = true;
    }
  }
  Serial.println(found ? "" : "nothing answered");

  if (!tpFound) {
    Serial.println("touch:      FAIL, no chip at 0x38. Check CTP_SDA, CTP_SCL, CTP_RST, VCC, GND.");
    return;
  }
  uint8_t chip = 0, fw = 0, vendor = 0;
  tpRead(0xA3, &chip, 1);
  tpRead(0xA6, &fw, 1);
  tpRead(0xA8, &vendor, 1);
  Serial.printf("touch:      chip at 0x38, chip id 0x%02X (FT6336U = 0x64), firmware 0x%02X, vendor 0x%02X\n",
                chip, fw, vendor);
  attachInterrupt(digitalPinToInterrupt(PIN_TP_INT), onTouchInt, FALLING);
}

// One touch point in screen coordinates. Returns false when nothing is touching.
static bool touchGet(int &sx, int &sy, int &rawX, int &rawY) {
  if (!tpFound) return false;
  uint8_t b[5];
  if (!tpRead(0x02, b, 5)) return false;
  const uint8_t count = b[0] & 0x0F;
  if (count == 0 || count > 2) return false;
  rawX = ((b[1] & 0x0F) << 8) | b[2];           // 0..319, panel in portrait
  rawY = ((b[3] & 0x0F) << 8) | b[4];           // 0..479
  int x = rawX, y = rawY, w = 320, h = 480;
  if (TOUCH_SWAP_XY) { int t = x; x = y; y = t; w = 480; h = 320; }
  if (TOUCH_FLIP_X) x = w - 1 - x;
  if (TOUCH_FLIP_Y) y = h - 1 - y;
  sx = x;
  sy = y;
  return true;
}

// ---- Test screens ---------------------------------------------------------------
static void drawTestCard() {
  const uint16_t bars[8] = {RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, BLACK};
  for (int i = 0; i < 8; i++) fillRect(i * 60, 0, 60, 200, bars[i]);
  for (int i = 0; i < 32; i++) {                // gray ramp, black on the left
    const uint8_t v = (uint8_t)(i * 255 / 31);
    fillRect(i * 15, 200, 15, 120, rgb(v, v, v));
  }
  frame(WHITE, 1);                              // must be visible on all four edges
}

const int TARGET = 64;
static const int targetX[4] = {0, SCREEN_W - TARGET, SCREEN_W - TARGET, 0};
static const int targetY[4] = {0, 0, SCREEN_H - TARGET, SCREEN_H - TARGET};
static const char *targetName[4] = {"top-left", "top-right", "bottom-right", "bottom-left"};

static void drawTargets(int current) {
  for (int i = 0; i < 4; i++) {
    const uint16_t c = i < current ? GREEN : (i == current ? WHITE : rgb(40, 40, 40));
    fillRect(targetX[i], targetY[i], TARGET, TARGET, c);
  }
}

enum Phase { CARD, CORNERS, DRAW };
static Phase phase = CARD;
static int corner = 0;
static bool wasDown = false;
static uint32_t lastHint = 0, touchSamples = 0;

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== dock_display ===");
  Serial.printf("psram:      %lu bytes\n", (unsigned long)ESP.getPsramSize());

  ledcAttach(PIN_LCD_BL, 5000, 8);              // 5 kHz, 8 bits
  backlight(0);

  touchInit();

  lcdInit();
  fillRect(0, 0, SCREEN_W, SCREEN_H, WHITE);
  for (int v = 0; v <= 255; v += 5) { backlight((uint8_t)v); delay(20); }  // fade up over 1 s
  Serial.println("backlight:  faded from off to full on a white screen");

  const uint16_t fills[3] = {RED, GREEN, BLUE};
  const char *names[3] = {"red", "green", "blue"};
  for (int i = 0; i < 3; i++) {
    const uint32_t t0 = micros();
    fillRect(0, 0, SCREEN_W, SCREEN_H, fills[i]);
    Serial.printf("fill:       %-5s full screen in %lu ms\n", names[i], (unsigned long)((micros() - t0) / 1000));
    delay(700);
  }

  drawTestCard();
  Serial.println("test card:  8 bars left to right = red, green, blue, yellow, cyan, magenta, white, black;");
  Serial.println("            below them a gray ramp, black on the left; a thin white line on all four edges.");
  Serial.println("NEXT:       touch the screen anywhere to start the corner test.");
}

void loop() {
  int sx = 0, sy = 0, rx = 0, ry = 0;
  const bool down = touchGet(sx, sy, rx, ry);

  if (down) {
    touchSamples++;
    if (!wasDown) {
      Serial.printf("touch down: raw x=%3d y=%3d -> screen x=%3d y=%3d  (INT pulses so far: %lu)\n",
                    rx, ry, sx, sy, (unsigned long)tpIntCount);
    }
    if (phase == CARD) {
      if (!wasDown) {
        fillRect(0, 0, SCREEN_W, SCREEN_H, BLACK);
        frame(WHITE, 1);
        drawTargets(0);
        phase = CORNERS;
        Serial.printf("NEXT:       tap the white square (%s).\n", targetName[0]);
      }
    } else {
      fillRect(sx - 2, sy - 2, 5, 5, YELLOW);   // a dot where the firmware thinks the finger is
      if (phase == CORNERS && !wasDown &&
          sx >= targetX[corner] && sx < targetX[corner] + TARGET &&
          sy >= targetY[corner] && sy < targetY[corner] + TARGET) {
        Serial.printf("corner:     %s ok\n", targetName[corner]);
        corner++;
        drawTargets(corner);
        if (corner == 4) {
          phase = DRAW;
          frame(GREEN, 6);
          const bool intOk = tpIntCount > 0;
          Serial.println("corners:    4 of 4");
          Serial.printf("touch INT:  %lu pulses -> %s\n", (unsigned long)tpIntCount,
                        intOk ? "ok" : "NONE, check the CTP_INT wire (touch still works by polling)");
          Serial.printf("RESULT: %s (touch). The picture is judged by eye; see README.\n", intOk ? "PASS" : "FAIL");
          Serial.println("NEXT:       draw with a finger; the yellow line should follow it with no gaps.");
        } else {
          Serial.printf("NEXT:       tap the white square (%s).\n", targetName[corner]);
        }
      }
    }
  }
  wasDown = down;

  if (millis() - lastHint > 5000) {
    lastHint = millis();
    if (!tpFound) Serial.println("waiting:    no touch chip found; fix the wiring and press the board's RST button.");
    else if (phase == CARD) Serial.println("waiting:    touch the screen anywhere to start the corner test.");
    else if (phase == CORNERS) Serial.printf("waiting:    tap the white square (%s). If the yellow dot lands somewhere else, report the raw numbers.\n", targetName[corner]);
  }
  delay(8);
}
