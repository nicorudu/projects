#include "ui_text.h"

#include <stdio.h>

namespace agent_ui {

namespace {

// Latin-1 Supplement, U+00C0..U+00FF, with the accents taken off. '\0' means "no plain form".
const char *const LATIN1_FOLD[64] = {
    "A", "A", "A", "A", "A", "A", "AE", "C", "E", "E", "E", "E", "I", "I", "I", "I",
    "D", "N", "O", "O", "O", "O", "O",  "x", "O", "U", "U", "U", "U", "Y", "Th", "ss",
    "a", "a", "a", "a", "a", "a", "ae", "c", "e", "e", "e", "e", "i", "i", "i", "i",
    "d", "n", "o", "o", "o", "o", "o",  "/", "o", "u", "u", "u", "u", "y", "th", "y",
};

// Decodes one UTF-8 code point at p and moves p past it. Bad bytes come back as U+FFFD.
uint32_t next_codepoint(const unsigned char *&p) {
  const uint32_t c = *p++;
  if (c < 0x80) return c;
  int extra;
  uint32_t cp;
  if ((c & 0xE0) == 0xC0) { extra = 1; cp = c & 0x1F; }
  else if ((c & 0xF0) == 0xE0) { extra = 2; cp = c & 0x0F; }
  else if ((c & 0xF8) == 0xF0) { extra = 3; cp = c & 0x07; }
  else return 0xFFFD;
  for (int i = 0; i < extra; i++) {
    if ((*p & 0xC0) != 0x80) return 0xFFFD;  // cut short (this also stops at the end of the string)
    cp = (cp << 6) | (*p++ & 0x3F);
  }
  return cp;
}

}  // namespace

std::string clean_text(const char *utf8, bool keep_newlines) {
  std::string out;
  if (!utf8) return out;
  const unsigned char *p = reinterpret_cast<const unsigned char *>(utf8);
  bool last_unknown = false;
  while (*p) {
    const uint32_t cp = next_codepoint(p);
    bool unknown = false;
    if (cp == '\n') out += keep_newlines ? '\n' : ' ';
    else if (cp == '\t') out += ' ';
    else if (cp == '\r') {}
    else if (cp < 0x20 || cp == 0x7F) {}                          // other control characters
    else if (cp < 0x7F) out += static_cast<char>(cp);
    else if (cp == 0x2022 || cp == 0x00B7 || cp == 0x2219 || cp == 0x25CF) out += "\xE2\x80\xA2";  // bullet
    else if (cp == 0x00A0 || cp == 0x202F || (cp >= 0x2000 && cp <= 0x200A)) out += ' ';  // odd spaces
    else if (cp == 0x2018 || cp == 0x2019 || cp == 0x2032) out += '\'';
    else if (cp == 0x201C || cp == 0x201D || cp == 0x2033 || cp == 0x00AB || cp == 0x00BB) out += '"';
    else if (cp == 0x2010 || cp == 0x2011 || cp == 0x2012 || cp == 0x2013 || cp == 0x2014 || cp == 0x2212) out += '-';
    else if (cp == 0x2026) out += "...";
    else if (cp == 0x2192) out += "->";
    else if (cp == 0x2190) out += "<-";
    else if (cp == 0x2713 || cp == 0x2714) out += "ok";
    else if (cp == 0x00BF) out += '?';
    else if (cp == 0x00A1) out += '!';
    else if (cp >= 0x00C0 && cp <= 0x00FF) out += LATIN1_FOLD[cp - 0x00C0];
    else if (cp == 0x200B || cp == 0x200C || cp == 0x200D || cp == 0xFEFF || (cp >= 0xFE00 && cp <= 0xFE0F)) {}  // joiners
    else unknown = true;
    if (unknown && !last_unknown) out += '?';  // one mark for a run (an emoji is several code points)
    last_unknown = unknown;
  }
  return out;
}

std::string duration(int64_t s) {
  if (s < 0) s = 0;
  char buf[32];
  if (s < 60) snprintf(buf, sizeof buf, "%ds", static_cast<int>(s));
  else if (s < 3600) snprintf(buf, sizeof buf, "%dm %ds", static_cast<int>(s / 60), static_cast<int>(s % 60));
  else snprintf(buf, sizeof buf, "%dh %dm", static_cast<int>(s / 3600), static_cast<int>(s % 3600 / 60));
  return buf;
}

std::string age(int64_t s) {
  if (s < 0) s = 0;
  char buf[24];
  if (s < 60) snprintf(buf, sizeof buf, "%ds", static_cast<int>(s));
  else if (s < 3600) snprintf(buf, sizeof buf, "%dm", static_cast<int>(s / 60));
  else if (s < 86400) snprintf(buf, sizeof buf, "%dh", static_cast<int>(s / 3600));
  else snprintf(buf, sizeof buf, "%dd", static_cast<int>(s / 86400));
  return buf;
}

std::string upper(const char *s) {
  std::string out;
  for (; s && *s; s++) out += (*s >= 'a' && *s <= 'z') ? static_cast<char>(*s - 32) : *s;
  return out;
}

}  // namespace agent_ui
