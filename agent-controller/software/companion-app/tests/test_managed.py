"""Managed sessions (the old main.py) against a stand-in `claude` that prints stream-json."""

import os
import stat
import sys

import pytest

from companion.core.app import App
from companion.platforms.claude_code.managed import run_task

FAKE_CLAUDE = r'''#!{python}
import json, sys
assert "--dangerously-skip-permissions" not in sys.argv, "permissions must not be skipped"
for m in [
    {{"type": "system", "subtype": "init", "session_id": "m1", "cwd": "/work/demo"}},
    {{"type": "assistant", "session_id": "m1", "message": {{"content": [
        {{"type": "tool_use", "name": "Bash", "input": {{"command": "ls"}}}}]}}}},
    {{"type": "assistant", "session_id": "m1", "message": {{"content": [{{"type": "text", "text": "Listed it."}}]}}}},
    {{"type": "result", "session_id": "m1", "is_error": False, "result": "Done: 3 files."}},
]:
    print(json.dumps(m), flush=True)
'''


@pytest.mark.skipif(os.name == "nt", reason="uses a shebang script")
async def test_managed_task_updates_session(tmp_path, cfg):
    script = tmp_path / "claude"
    script.write_text(FAKE_CLAUDE.format(python=sys.executable))
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    app = App(cfg)
    sid = await run_task(app, "list files", claude_bin=str(script))
    assert sid == "m1"
    s = app.state.sessions["m1"]
    assert s.name == "demo" and s.status.value == "done" and s.text == "Done: 3 files."
