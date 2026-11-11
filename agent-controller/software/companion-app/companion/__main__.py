"""python -m companion [run | install-hooks | uninstall-hooks | doctor]"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import signal
import sys
import urllib.request
from pathlib import Path

from . import __version__, config
from .core.app import App
from .hooks import install as hook_install
from .hooks.server import HookServer
from .platforms.claude_code.attached import ClaudeCode
from .transports.websocket import WebSocketTransport

log = logging.getLogger("companion")


async def run(cfg: config.Config) -> None:
    app = App(cfg)
    claude = ClaudeCode()
    app.register_platform(claude)
    ws = WebSocketTransport(app, cfg.ws_host, cfg.ws_port)
    hooks = HookServer(claude, cfg.hook_host, cfg.hook_port)
    await app.start()
    await ws.start()
    await hooks.start()
    print(f"Agent controller companion {__version__}")
    print(f"  devices connect to   ws://<this computer>:{ws.port}")
    print(f"  Claude Code hooks to http://{cfg.hook_host}:{hooks.port}/hooks/claude"
          f"  ({hook_install.installed_count()} hooks installed)")
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
        await hooks.stop()
        await ws.stop()
        await app.stop()  # any approval still waiting gets "no decision" → normal prompt


def doctor(cfg: config.Config, settings: Path) -> None:
    print(f"companion {__version__} on Python {sys.version.split()[0]} ({sys.executable})")
    print(f"Claude Code settings: {settings} ({'found' if settings.exists() else 'not found'})")
    n = hook_install.installed_count(settings)
    print(f"our hooks installed: {n}" + ("" if n else "  → run: python -m companion install-hooks"))
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://{cfg.hook_host}:{cfg.hook_port}/health", timeout=1) as r:
            print(f"companion app: running ({json.loads(r.read())})")
    except OSError:
        print("companion app: not running  → run: python -m companion")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m companion", description="AI Agent Controller companion app")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="run the companion app (default)")
    r.add_argument("--ws-port", type=int)
    r.add_argument("--hook-port", type=int)
    for name, text in (("install-hooks", "add our hooks to ~/.claude/settings.json (backs it up first)"),
                       ("uninstall-hooks", "remove our hooks (backs the file up first)"),
                       ("doctor", "check the setup")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--settings", type=Path, default=hook_install.CLAUDE_SETTINGS)
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    cfg = config.load(ws_port=getattr(args, "ws_port", None), hook_port=getattr(args, "hook_port", None))

    if args.cmd == "install-hooks":
        backup = hook_install.install(cfg, args.settings)
        print(f"Installed {hook_install.installed_count(args.settings)} hooks into {args.settings}")
        print(f"Backup: {backup}" if backup else "(no existing file, nothing to back up)")
        print("Restart any running Claude Code sessions so they pick the hooks up.")
    elif args.cmd == "uninstall-hooks":
        removed, backup = hook_install.uninstall(args.settings)
        print(f"Removed {removed} hooks from {args.settings}" + (f"\nBackup: {backup}" if backup else ""))
    elif args.cmd == "doctor":
        doctor(cfg, args.settings)
    else:
        try:
            asyncio.run(run(cfg))
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
