"""python -m companion [run | install-hooks | uninstall-hooks]"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys

from . import __version__, config
from .core.app import App
from .transports.websocket import WebSocketTransport

log = logging.getLogger("companion")


async def run(cfg: config.Config) -> None:
    app = App(cfg)
    ws = WebSocketTransport(app, cfg.ws_host, cfg.ws_port)
    await app.start()
    await ws.start()
    print(f"Agent controller companion {__version__}")
    print(f"  devices connect to ws://<this computer>:{ws.port}")
    print("  Ctrl-C to quit")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):  # Windows
            pass
    try:
        await stop.wait()
    finally:
        await ws.stop()
        await app.stop()


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m companion", description="AI Agent Controller companion app")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="run the companion app (default)")
    r.add_argument("--ws-port", type=int)
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    cfg = config.load(ws_port=getattr(args, "ws_port", None))
    try:
        asyncio.run(run(cfg))
    except KeyboardInterrupt:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
