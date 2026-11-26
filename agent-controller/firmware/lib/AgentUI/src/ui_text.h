// Text helpers with no LVGL in them, so they can be tested on their own.
#pragma once

#include <stdint.h>
#include <string>

namespace agent_ui {

// Make text safe for the built-in fonts, which only hold ASCII and a bullet.
// Smart quotes, dashes and ellipses become their ASCII forms, accented Latin letters lose
// their accent, and anything else (emoji, other scripts) becomes '?'.
// Newlines are kept when keep_newlines is true, otherwise they become spaces.
std::string clean_text(const char *utf8, bool keep_newlines);

// "45s", "6m 24s", "1h 2m".
std::string duration(int64_t seconds);

// "45s", "6m", "2h", "3d": how long ago, short.
std::string age(int64_t seconds);

// "working" -> "WORKING".
std::string upper(const char *s);

}  // namespace agent_ui
