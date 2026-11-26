// Colors, fonts and sizes. Blueprint rev 3 section 7.2; the exact values are our choices.
#pragma once

#include <lvgl.h>

namespace agent_ui {
namespace theme {

constexpr uint32_t BG = 0x0B0D10;        // near-black background
constexpr uint32_t PANEL = 0x14171C;     // rows, boxes
constexpr uint32_t PANEL_HI = 0x1C2027;  // the selected option
constexpr uint32_t TEXT = 0xF2F4F7;      // titles
constexpr uint32_t TEXT_SOFT = 0xC5CAD3; // body text
constexpr uint32_t TEXT_DIM = 0x8A9099;  // labels, hints

constexpr uint32_t WORKING = 0x4DA3FF;
constexpr uint32_t WAITING = 0xF5C542;
constexpr uint32_t DONE = 0x3DDC84;
constexpr uint32_t ERROR_C = 0xFF5A5F;
constexpr uint32_t READY = 0x4FD1C5;     // proposed in M1b; confirm against the reference
constexpr uint32_t IDLE = 0x8A9099;
constexpr uint32_t RECORDING = 0xFFFFFF;

constexpr int HEADER_H = 36;
constexpr int ROW_H = 62;       // four rows show at once
constexpr int ROW_GAP = 8;
constexpr int MARGIN = 8;
constexpr int RADIUS = 8;
constexpr int OUTLINE = 2;      // the selected row's outline
constexpr int SCROLL_STEP = 48; // pixels the detail page moves for one stick flick

inline const lv_font_t *font_small() { return &lv_font_montserrat_12; }
inline const lv_font_t *font_label() { return &lv_font_montserrat_14; }
inline const lv_font_t *font_body() { return &lv_font_montserrat_16; }
inline const lv_font_t *font_title() { return &lv_font_montserrat_20; }

}  // namespace theme
}  // namespace agent_ui
