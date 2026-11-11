import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parents[1] / "tools"))  # agent-controller/tools (fake_device)

from companion.config import Config  # noqa: E402
from companion.core.app import App  # noqa: E402
from companion.transports.websocket import WebSocketTransport  # noqa: E402


@pytest.fixture
def cfg():
    return Config(ws_host="127.0.0.1", ws_port=0, hook_port=0, heartbeat_timeout_s=0.6,
                  approval_timeout_s=3.0, alert_sound=True)


@pytest.fixture
async def running(cfg):
    """A started App + WebSocket transport on a free port. Yields (app, ws_url)."""
    app = App(cfg)
    ws = WebSocketTransport(app, cfg.ws_host, 0)
    await app.start()
    await ws.start()
    yield app, f"ws://127.0.0.1:{ws.port}"
    await ws.stop()
    await app.stop()
