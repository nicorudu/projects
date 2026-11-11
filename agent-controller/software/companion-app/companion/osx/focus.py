"""Bring a Claude Code session's terminal tab to the front on macOS.

Terminal.app and iTerm2: finds the tab by its TTY. Anything else (Cursor, VS Code, Warp,
Ghostty…): activates the app by bundle id. Needs no special permission; macOS may ask once
to let the companion app control Terminal/iTerm (Automation).
"""

from __future__ import annotations

import re
import subprocess

_TTY = re.compile(r"/dev/tty[a-z]*\d+")
_BUNDLE = re.compile(r"[A-Za-z0-9.\-]+")

TERMINAL_SCRIPT = """
tell application "Terminal"
  activate
  repeat with w in windows
    repeat with t in tabs of w
      if tty of t is "{tty}" then
        set selected of t to true
        set index of w to 1
        return "ok"
      end if
    end repeat
  end repeat
end tell
return "missing"
"""

ITERM_SCRIPT = """
tell application "iTerm2"
  activate
  repeat with w in windows
    repeat with t in tabs of w
      repeat with s in sessions of t
        if tty of s is "{tty}" then
          select w
          tell t to select
          tell s to select
          return "ok"
        end if
      end repeat
    end repeat
  end repeat
end tell
return "missing"
"""


def _osascript(script: str) -> str:
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=4)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip()


def focus_terminal(term: dict) -> bool:
    tty = term.get("tty", "")
    prog = term.get("term_program", "")
    bundle = term.get("bundle_id", "")
    if tty and _TTY.fullmatch(tty):
        if prog == "Apple_Terminal" and _osascript(TERMINAL_SCRIPT.format(tty=tty)) == "ok":
            return True
        if prog == "iTerm.app" and _osascript(ITERM_SCRIPT.format(tty=tty)) == "ok":
            return True
    if bundle and _BUNDLE.fullmatch(bundle):
        return _osascript(f'tell application id "{bundle}" to activate\nreturn "ok"') == "ok"
    return False
