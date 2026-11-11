"""Settings. Defaults live here; ~/.agent-controller/config.toml can override any of them.

API keys never go in this file. They are stored in the OS keychain (added in M2).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, fields, replace
from pathlib import Path

HOME_DIR = Path.home() / ".agent-controller"
CONFIG_PATH = HOME_DIR / "config.toml"


@dataclass(frozen=True)
class Config:
    # Device link (Path A, Wi-Fi WebSocket). 0.0.0.0 so the dock can reach it over the LAN.
    ws_host: str = "0.0.0.0"
    ws_port: int = 8765
    # Claude Code hook server. Always loopback only.
    hook_host: str = "127.0.0.1"
    hook_port: int = 8766
    # Heartbeat (protocol v1): devices ping every 500 ms; 2 s of silence = link down.
    heartbeat_timeout_s: float = 2.0
    hello_timeout_s: float = 3.0
    # How long an approval waits for a key press before Claude Code shows its own prompt.
    approval_timeout_s: float = 120.0
    # Hook timeout written into ~/.claude/settings.json for PermissionRequest (must exceed the above).
    permission_hook_timeout_s: int = 600
    # Timeout for the status hooks; short so a stuck app can never slow Claude Code down.
    status_hook_timeout_s: int = 2
    # Play the alert sound when a session starts waiting.
    alert_sound: bool = True

    @property
    def hook_url(self) -> str:
        return f"http://{self.hook_host}:{self.hook_port}/hooks/claude"


def load(path: Path = CONFIG_PATH, **overrides) -> Config:
    """Defaults, then the TOML file (if any), then explicit overrides (CLI flags, tests)."""
    cfg = Config()
    if path.exists():
        data = tomllib.loads(path.read_text())
        known = {f.name for f in fields(Config)}
        cfg = replace(cfg, **{k: v for k, v in data.items() if k in known})
    overrides = {k: v for k, v in overrides.items() if v is not None}
    return replace(cfg, **overrides)
