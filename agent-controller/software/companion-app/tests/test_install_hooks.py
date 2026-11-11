import json

from companion.config import Config
from companion.hooks import install as hi

HOOKS = 10  # PermissionRequest + 9 status events

USER_SETTINGS = {
    "model": "opus",
    "permissions": {"allow": ["Bash(npm test)"]},
    "hooks": {
        "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "~/bin/audit.sh"}]}],
        "Stop": [{"hooks": [{"type": "command", "command": "say done"}]}],
    },
}


def test_install_keeps_user_settings_is_idempotent_and_uninstalls_cleanly(tmp_path):
    path = tmp_path / ".claude" / "settings.json"
    path.parent.mkdir()
    path.write_text(json.dumps(USER_SETTINGS))
    cfg = Config()

    backup = hi.install(cfg, path, python="/usr/bin/python3")
    assert backup and json.loads(backup.read_text()) == USER_SETTINGS
    data = json.loads(path.read_text())
    assert data["model"] == "opus" and data["permissions"] == USER_SETTINGS["permissions"]
    assert data["hooks"]["PreToolUse"][0] == USER_SETTINGS["hooks"]["PreToolUse"][0]  # user's hook first
    assert hi.installed_count(path) == HOOKS

    perm = data["hooks"]["PermissionRequest"][0]["hooks"][0]
    assert perm == {"type": "command", "timeout": 600, "command":
                    '"/usr/bin/python3" -m companion.hooks.report --url http://127.0.0.1:8766/hooks/claude --wait'}
    for event in ("SessionStart", "PreToolUse", "Stop"):
        h = data["hooks"][event][-1]["hooks"][0]  # ours come after the user's own hooks
        assert h["type"] == "command" and h["async"] is True and "--wait" not in h["command"]
    # nothing uses Claude Code's http hook type any more (it prints errors when the app is off)
    assert all(h["type"] == "command" for groups in data["hooks"].values() for g in groups for h in g["hooks"]
               if hi.is_ours(h))

    hi.install(cfg, path, python="/usr/bin/python3")  # again: no duplicates
    assert hi.installed_count(path) == HOOKS

    removed, _ = hi.uninstall(path)
    assert removed == HOOKS
    assert json.loads(path.read_text()) == USER_SETTINGS


def test_install_into_missing_file(tmp_path):
    path = tmp_path / "settings.json"
    assert hi.install(Config(), path) is None
    assert hi.installed_count(path) == HOOKS
    hi.uninstall(path)
    assert json.loads(path.read_text()) == {}


def test_is_ours_is_narrow():
    assert hi.is_ours({"type": "http", "url": "http://localhost:8766/hooks/claude"})
    assert not hi.is_ours({"type": "http", "url": "https://example.com/hooks/claude"})
    assert not hi.is_ours({"type": "command", "command": "python -m something.else"})


def test_reinstall_replaces_the_old_http_hooks(tmp_path):
    path = tmp_path / "settings.json"
    old = {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
        {"type": "http", "url": "http://127.0.0.1:8766/hooks/claude", "timeout": 2}]}]}}
    path.write_text(json.dumps(old))
    hi.install(Config(), path)
    data = json.loads(path.read_text())
    assert [h["type"] for g in data["hooks"]["PreToolUse"] for h in g["hooks"]] == ["command"]
