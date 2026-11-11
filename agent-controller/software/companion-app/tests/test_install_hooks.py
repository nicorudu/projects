import json

from companion.config import Config
from companion.hooks import install as hi

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
    assert hi.installed_count(path) == 9

    perm = data["hooks"]["PermissionRequest"][0]["hooks"][0]
    assert perm == {"type": "http", "url": "http://127.0.0.1:8766/hooks/claude", "timeout": 600}
    start = data["hooks"]["SessionStart"][0]["hooks"][0]
    assert start["type"] == "command" and start["async"] is True
    assert start["command"].startswith('"/usr/bin/python3" -m companion.hooks.report')

    hi.install(cfg, path, python="/usr/bin/python3")  # again: no duplicates
    assert hi.installed_count(path) == 9

    removed, _ = hi.uninstall(path)
    assert removed == 9
    assert json.loads(path.read_text()) == USER_SETTINGS


def test_install_into_missing_file(tmp_path):
    path = tmp_path / "settings.json"
    assert hi.install(Config(), path) is None
    assert hi.installed_count(path) == 9
    hi.uninstall(path)
    assert json.loads(path.read_text()) == {}


def test_is_ours_is_narrow():
    assert hi.is_ours({"type": "http", "url": "http://localhost:8766/hooks/claude"})
    assert not hi.is_ours({"type": "http", "url": "https://example.com/hooks/claude"})
    assert not hi.is_ours({"type": "command", "command": "python -m something.else"})
