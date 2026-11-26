#!/usr/bin/env python3
"""Runs the dock simulator and connects it to the companion app.

The simulator (firmware/sim) talks like the dock on its USB link: one JSON message per line
on stdin and stdout. This script starts it and passes those lines to and from the app's
WebSocket, so the real screens show your real sessions.

    cd firmware/sim && make          # once, and after changing the screens
    python -m companion              # in another terminal (software/companion-app)
    python tools/sim_bridge.py       # opens the window

Keys in the window: arrows = stick, s = Send, c = Cancel, v = Voice, g = green, Esc = quit.
If the app isn't running, the window says so and connects by itself once it starts.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIM = ROOT / "firmware" / "sim" / "build" / "agent-sim"


async def run(url: str, sim_path: Path, zoom: float) -> int:
    if not sim_path.exists():
        print(f"The simulator isn't built yet. Run:  cd {sim_path.parents[1]} && make", file=sys.stderr)
        return 1
    sim = await asyncio.create_subprocess_exec(str(sim_path), "--zoom", str(zoom),
                                               stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    ws = None           # the open connection to the app, or None
    said_hello = False  # the app wants "hello" first on every new connection

    async def sim_to_app() -> None:
        nonlocal said_hello
        while line := await sim.stdout.readline():
            text = line.decode("utf-8", "replace").strip()
            if not text or ws is None:
                continue
            if not said_hello:
                try:
                    if json.loads(text).get("t") != "hello":
                        continue  # the simulator repeats its hello every second while the link is down
                except json.JSONDecodeError:
                    continue
                said_hello = True
            try:
                await ws.send(text)
            except ConnectionClosed:
                pass

    async def app_to_sim() -> None:
        nonlocal ws, said_hello
        while True:
            try:
                async with connect(url) as conn:
                    ws, said_hello = conn, False
                    print(f"connected to {url}", file=sys.stderr)
                    async for message in conn:
                        if isinstance(message, str):  # binary frames are audio; the simulator has no speaker
                            sim.stdin.write(message.encode() + b"\n")
                            await sim.stdin.drain()
            except (OSError, ConnectionClosed):
                pass
            if ws is not None:
                print("the companion app went away; waiting for it", file=sys.stderr)
            ws = None
            await asyncio.sleep(1.0)

    tasks = [asyncio.create_task(sim_to_app()), asyncio.create_task(app_to_sim())]
    try:
        await sim.wait()  # the window was closed
    finally:
        for t in tasks:
            t.cancel()
        if sim.returncode is None:
            sim.terminate()
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="ws://localhost:8765", help="the companion app's device address")
    ap.add_argument("--sim", type=Path, default=DEFAULT_SIM, help="path to the agent-sim program")
    ap.add_argument("--zoom", type=float, default=2.0, help="window size: 1 = 480 x 320 pixels, 2 = double")
    args = ap.parse_args()
    try:
        sys.exit(asyncio.run(run(args.url, args.sim, args.zoom)))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
