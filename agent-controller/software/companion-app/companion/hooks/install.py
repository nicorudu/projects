"""Add or remove our hooks in ~/.claude/settings.json.

- Backs the file up first (settings.json.agent-controller-backup-<time>).
- Only touches hooks it recognizes as ours; your other hooks and settings stay as they are.
- Running install twice doesn't duplicate anything.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from ..config import Config

CLAUDE_SETTINGS = Path.home() / ".claude" / "settings.json"
REPORT_MODULE = "companion.hooks.report"

# Events we listen to over HTTP, and whether they take a tool matcher.
HTTP_EVENTS = {
    "UserPromptSubmit": False,
    "PreToolUse": True,
    "PostToolUse": True,
    "Notification": False,
    "Stop": False,
    "StopFailure": False,
    "SessionEnd": False,
}


def python_command(python: str) -> str:
    p = Path(python).as_posix() if os.name == "nt" else python
    return f'"{p}" -m {REPORT_MODULE}'


def build_hooks(cfg: Config, python: str = sys.executable) -> dict[str, list[dict]]:
    url = cfg.hook_url
    out: dict[str, list[dict]] = {
        # SessionStart only accepts command hooks. Async so it never delays startup.
        "SessionStart": [{"hooks": [{"type": "command", "command": f"{python_command(python)} --url {url}",
                                     "async": True, "timeout": 5}]}],
        "PermissionRequest": [{"matcher": "*", "hooks": [
            {"type": "http", "url": url, "timeout": cfg.permission_hook_timeout_s}]}],
    }
    for event, has_matcher in HTTP_EVENTS.items():
        group: dict = {"hooks": [{"type": "http", "url": url, "timeout": cfg.status_hook_timeout_s}]}
        if has_matcher:
            group = {"matcher": "*", **group}
        out[event] = [group]
    return out


def is_ours(hook: dict) -> bool:
    if hook.get("type") == "http":
        u = urlparse(hook.get("url", ""))
        return u.hostname in ("127.0.0.1", "localhost") and u.path == "/hooks/claude"
    if hook.get("type") == "command":
        return REPORT_MODULE in hook.get("command", "")
    return False


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text()
    if not text.strip():
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} isn't a JSON object; not touching it")
    return data


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    dest = path.with_name(f"{path.name}.agent-controller-backup-{time.strftime('%Y%m%d-%H%M%S')}")
    n = 1
    while dest.exists():
        dest = dest.with_name(f"{dest.name}-{n}")
        n += 1
    dest.write_bytes(path.read_bytes())
    return dest


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, path)


def _strip(data: dict) -> int:
    """Remove our hooks from a settings dict in place. Returns how many were removed."""
    removed = 0
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return 0
    for event in list(hooks):
        groups = hooks[event]
        if not isinstance(groups, list):
            continue
        kept_groups = []
        for g in groups:
            if not isinstance(g, dict) or not isinstance(g.get("hooks"), list):
                kept_groups.append(g)
                continue
            kept = [h for h in g["hooks"] if not (isinstance(h, dict) and is_ours(h))]
            removed += len(g["hooks"]) - len(kept)
            if kept:
                kept_groups.append({**g, "hooks": kept})
        if kept_groups:
            hooks[event] = kept_groups
        else:
            del hooks[event]
    if not hooks:
        del data["hooks"]
    return removed


def install(cfg: Config, path: Path = CLAUDE_SETTINGS, python: str = sys.executable) -> Path | None:
    data = _load(path)
    backup = _backup(path)
    _strip(data)
    hooks = data.setdefault("hooks", {})
    for event, groups in build_hooks(cfg, python).items():
        hooks.setdefault(event, []).extend(groups)
    _write(path, data)
    return backup


def uninstall(path: Path = CLAUDE_SETTINGS) -> tuple[int, Path | None]:
    if not path.exists():
        return 0, None
    data = _load(path)
    backup = _backup(path)
    removed = _strip(data)
    _write(path, data)
    return removed, backup


def installed_count(path: Path = CLAUDE_SETTINGS) -> int:
    try:
        data = _load(path)
    except (ValueError, OSError):
        return 0
    return sum(1 for groups in (data.get("hooks") or {}).values() if isinstance(groups, list)
               for g in groups if isinstance(g, dict)
               for h in g.get("hooks", []) if isinstance(h, dict) and is_ours(h))
