"""What a session is called: the task title, then the repo name, then the folder name."""

import asyncio
import subprocess

from companion.core.app import App
from companion.core.names import repo_from_url, repo_label, short_title
from companion.view import builder


def test_short_title():
    assert short_title("fix the login bug") == "fix the login bug"
    assert short_title("  fix   the\tlogin bug \n\nand also the logout path") == "fix the login bug"
    assert short_title("/clear") == "" and short_title("") == "" and short_title(None) == ""
    long = short_title("please go through every file in the repository and rename the old helper to the new name")
    assert long.endswith("…") and len(long) <= 61 and not long[:-1].endswith(" ")
    assert long.startswith("please go through every file")


def test_repo_from_url():
    assert repo_from_url("https://github.com/nicorudu/projects.git") == "projects"
    assert repo_from_url("git@github.com:nicorudu/projects.git") == "projects"
    assert repo_from_url("https://github.com/nicorudu/projects/") == "projects"
    assert repo_from_url("") == "" and repo_from_url(None) == ""


def make_repo(path, remote="https://github.com/nicorudu/projects.git"):
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    if remote:
        subprocess.run(["git", "-C", str(path), "remote", "add", "origin", remote], check=True)


def test_repo_label(tmp_path):
    repo = tmp_path / "Imported Home Projects"  # the folder is not called what the repo is
    make_repo(repo)
    (repo / "mitzi" / "docs").mkdir(parents=True)
    assert repo_label(str(repo)) == "projects"
    assert repo_label(str(repo / "mitzi")) == "projects/mitzi"
    assert repo_label(str(repo / "mitzi" / "docs")) == "projects/docs"
    link = tmp_path / "link"
    link.symlink_to(repo)  # like ~/projects pointing at the external drive
    assert repo_label(str(link)) == "projects"

    make_repo(tmp_path / "no-remote", remote=None)
    assert repo_label(str(tmp_path / "no-remote")) == ""
    (tmp_path / "plain").mkdir()
    assert repo_label(str(tmp_path / "plain")) == ""
    assert repo_label(str(tmp_path / "missing")) == "" and repo_label("") == ""


async def wait_until(check, timeout=3.0):
    for _ in range(int(timeout / 0.02)):
        if check():
            return
        await asyncio.sleep(0.02)
    raise AssertionError("timed out")


async def test_rows_use_the_repo_name_then_the_folder_and_the_title_when_there_is_one(cfg, tmp_path):
    repo = tmp_path / "Imported Home Projects"
    make_repo(repo)
    (tmp_path / "scratch").mkdir()
    app = App(cfg)
    await app.start()
    a = app.upsert_session("claude_code", "a", cwd=str(repo), status="done")
    b = app.upsert_session("claude_code", "b", cwd=str(tmp_path / "scratch"), status="done")
    assert a.name == "Imported Home Projects"  # the folder name, until git has answered
    await wait_until(lambda: a.name == "projects")
    assert b.name == "scratch"  # no repo: the folder name stays
    rows = {r["id"]: r for r in builder.build(app.state)["rows"]}
    assert rows["a"]["title"] == "projects" and rows["b"]["title"] == "scratch"

    a.title = "Fix the login bug"
    rows = {r["id"]: r for r in builder.build(app.state)["rows"]}
    assert rows["a"]["title"] == "Fix the login bug" and rows["a"]["name"] == "projects"

    c = app.upsert_session("claude_code", "c123456", cwd=str(repo), status="done")  # same folder: asked once
    assert c.repo == "projects" and c.name == "projects ·c123"
    await app.stop()
