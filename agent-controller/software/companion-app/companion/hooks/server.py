"""Local HTTP server that Claude Code's hooks POST to: http://127.0.0.1:8766/hooks/claude

Loopback only. Requests must say Host: 127.0.0.1/localhost and send a JSON body, which stops
a web page in a browser from posting fake events to it.
"""

from __future__ import annotations

import asyncio
import json
import logging

from aiohttp import web

from .. import __version__

log = logging.getLogger(__name__)


class HookServer:
    def __init__(self, claude_plugin, host: str = "127.0.0.1", port: int = 8766):
        self.plugin = claude_plugin
        self.host = host
        self.port = port
        self._runner: web.AppRunner | None = None

    async def start(self) -> None:
        app = web.Application(client_max_size=4 * 1024 * 1024)
        app.router.add_post("/hooks/claude", self._claude)
        app.router.add_get("/health", self._health)
        self._runner = web.AppRunner(app, access_log=None)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.host, self.port)
        await site.start()
        self.port = site._server.sockets[0].getsockname()[1]
        log.info("hook server listening on http://%s:%d/hooks/claude", self.host, self.port)

    async def stop(self) -> None:
        if self._runner:
            await self._runner.cleanup()

    def _host_ok(self, request: web.Request) -> bool:
        host = (request.host or "").rsplit(":", 1)[0].strip("[]")
        return host in ("127.0.0.1", "localhost", "::1")

    async def _health(self, request: web.Request) -> web.Response:
        if not self._host_ok(request):
            return web.Response(status=403)
        return web.json_response({"ok": True, "app": "agent-controller", "version": __version__})

    async def _claude(self, request: web.Request) -> web.Response:
        if not self._host_ok(request):
            return web.Response(status=403)
        if request.content_type != "application/json":
            return web.Response(status=415)
        try:
            payload = json.loads(await request.text())
            if not isinstance(payload, dict):
                raise ValueError
        except ValueError:
            return web.Response(status=400)

        task = asyncio.create_task(self.plugin.handle_hook(payload))
        # Approvals can wait a long time; stop waiting if Claude Code hangs up.
        while True:
            done, _ = await asyncio.wait({task}, timeout=0.5)
            if done:
                break
            if request.transport is None or request.transport.is_closing():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
                return web.Response(status=499)
        try:
            result = task.result()
        except Exception:  # never let a bug block Claude Code: answer "no decision"
            log.exception("hook handler failed for %s", payload.get("hook_event_name"))
            result = {}
        return web.json_response(result)
