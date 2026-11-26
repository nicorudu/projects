// LVGL settings for the AI Agent Controller, shared by the dock and the simulator so both
// draw with the same fonts and color depth. Anything not set here keeps LVGL's default.
// LVGL finds this file by name; it must be on the include path.
#ifndef LV_CONF_H
#define LV_CONF_H

#define LV_COLOR_FORMAT_DEFAULT LV_COLOR_FORMAT_RGB565  // what the ST7796S is sent
#define LV_DEF_REFR_PERIOD 33        // about 30 frames a second
#define LV_DPI_DEF 130

// Use the C library's malloc (on the ESP32-S3 large blocks then come from PSRAM).
#define LV_USE_STDLIB_MALLOC LV_STDLIB_CLIB
#define LV_USE_STDLIB_STRING LV_STDLIB_CLIB
#define LV_USE_STDLIB_SPRINTF LV_STDLIB_CLIB

#define LV_USE_OS LV_OS_NONE         // LVGL is only ever called from one task

// Fonts used by AgentUI (ui_theme.h). Each one costs flash, so only these four.
#define LV_FONT_MONTSERRAT_12 1
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_MONTSERRAT_16 1
#define LV_FONT_MONTSERRAT_20 1
#define LV_FONT_DEFAULT &lv_font_montserrat_14

#define LV_USE_THEME_DEFAULT 1
#define LV_THEME_DEFAULT_DARK 1

#define LV_BUILD_EXAMPLES 0
#define LV_BUILD_DEMOS 0

#ifdef ARDUINO
#define LV_USE_LOG 0
#else
// Desktop simulator: an SDL window, and warnings on the terminal.
#define LV_USE_LOG 1
#define LV_LOG_LEVEL LV_LOG_LEVEL_WARN
#define LV_LOG_PRINTF 1
#define LV_USE_SDL 1
#define LV_SDL_INCLUDE_PATH <SDL2/SDL.h>
#define LV_SDL_RENDER_MODE LV_DISPLAY_RENDER_MODE_DIRECT
#define LV_SDL_BUF_COUNT 1
#define LV_SDL_ACCELERATED 1
#define LV_SDL_FULLSCREEN 0
#define LV_SDL_DIRECT_EXIT 1
#endif

#endif  // LV_CONF_H
