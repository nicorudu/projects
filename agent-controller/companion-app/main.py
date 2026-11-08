import asyncio
import json
import subprocess
import threading
import websockets

connected_device = None
claude_process = None

def start_claude(task):
    global claude_process
    claude_process = subprocess.Popen(
        ["claude", "--output-format", "stream-json", "--verbose", "--dangerously-skip-permissions", "--print", task],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    threading.Thread(target=read_claude_output, daemon=True).start()

def read_claude_output():
    for line in claude_process.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            asyncio.run(handle_claude_event(msg))
        except json.JSONDecodeError:
            pass

async def handle_claude_event(msg):
    global connected_device
    if connected_device is None:
        return
    t = msg.get("type")
    if t == "assistant":
        content = msg.get("message", {}).get("content", [])
        for block in content:
            if block.get("type") == "tool_use":
                await connected_device.send(json.dumps({
                    "t": "tool",
                    "tool": block.get("name", ""),
                    "input": str(block.get("input", ""))[:120]
                }))
            elif block.get("type") == "text":
                text = block.get("text", "").strip()
                if text:
                    await connected_device.send(json.dumps({
                        "t": "text",
                        "msg": text[:200]
                    }))
    elif t == "result":
        await connected_device.send(json.dumps({
            "t": "done",
            "result": msg.get("result", "")[:300],
            "error": msg.get("is_error", False)
        }))

async def handle_device(websocket):
    global connected_device
    connected_device = websocket
    print("Device connected")
    await websocket.send(json.dumps({"t": "pong"}))
    try:
        async for message in websocket:
            msg = json.loads(message)
            if msg.get("t") == "ping":
                await websocket.send(json.dumps({"t": "pong"}))
            elif msg.get("t") == "task":
                task = msg.get("task", "say hello")
                print(f"Starting task: {task}")
                await websocket.send(json.dumps({"t": "status", "msg": "running"}))
                start_claude(task)
    except websockets.exceptions.ConnectionClosed:
        print("Device disconnected")
        connected_device = None

async def main():
    print("Agent controller running on ws://localhost:8765")
    print("Waiting for device to connect...")
    async with websockets.serve(handle_device, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())