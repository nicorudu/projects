"""What a session is called: the task title, then the repo name, then the folder name."""

import asyncio
import os
import subprocess

from companion.core.app import App
from companion.core.names import project_folder, repo_from_url, repo_info, short_title
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


def test_repo_info_and_project_folder(tmp_path):
    repo = tmp_path / "Imported Home Projects"  # the folder is not called what the repo is
    make_repo(repo)
    (repo / "mitzi" / "docs").mkdir(parents=True)
    (repo / ".github").mkdir()
    top = os.path.realpath(repo)
    assert repo_info(str(repo)) == ("projects", top)
    assert repo_info(str(repo / "mitzi" / "docs")) == ("projects", top)
    link = tmp_path / "link"
    link.symlink_to(repo)  # like ~/projects pointing at the external drive
    assert repo_info(str(link)) == ("projects", top)

    assert project_folder(top, str(repo / "mitzi")) == "mitzi"
    assert project_folder(top, str(repo / "mitzi" / "docs")) == "mitzi"
    assert project_folder(top, str(link / "mitzi" / "docs")) == "mitzi"
    assert project_folder(top, str(repo)) == ""            # the repo's top is no project
    assert project_folder(top, str(repo / ".github")) == ""  # nor is a hidden folder
    assert project_folder(top, str(tmp_path)) == ""        # nor anywhere outside the repo
    assert project_folder("", str(repo / "mitzi")) == "" and project_folder(top, "") == ""

    make_repo(tmp_path / "no-remote", remote=None)
    assert repo_info(str(tmp_path / "no-remote")) == ("", "")
    (tmp_path / "plain").mkdir()
    assert repo_info(str(tmp_path / "plain")) == ("", "")
    assert repo_info(str(tmp_path / "missing")) == ("", "") and repo_info("") == ("", "")


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


async def test_the_row_is_named_after_the_project_folder_being_worked_in(cfg, tmp_path):
    """Nico, 2026-11-26: a session started at the repo's top and working in agent-controller
    should read "agent-controller". Earlier the same row flipped to "projects" on a `cd`."""
    repo = tmp_path / "Imported Home Projects"
    make_repo(repo)
    for d in ("agent-controller/software", "mitzi", ".github"):
        (repo / d).mkdir(parents=True)
    app = App(cfg)
    await app.start()
    home = str(repo)

    a = app.upsert_session("claude_code", "a", cwd=home, home=home, status="working")
    await wait_until(lambda: a.name == "projects")  # only ever at the top: the repo name

    app.upsert_session("claude_code", "a", cwd=str(repo / "agent-controller" / "software"), home=home)
    assert a.name == "agent-controller"
    app.upsert_session("claude_code", "a", cwd=home, home=home)  # back at the top: the name stays
    app.upsert_session("claude_code", "a", cwd=str(repo / ".github"), home=home)
    app.upsert_session("claude_code", "a", cwd=str(tmp_path), home=home)  # outside the repo
    assert a.name == "agent-controller"

    # Editing a file elsewhere moves it, without any `cd`. Reading is not passed as `touched`.
    app.upsert_session("claude_code", "a", cwd=str(tmp_path), home=home, touched=str(repo / "mitzi" / "plan.md"))
    assert a.name == "mitzi"
    app.upsert_session("claude_code", "a", cwd=str(tmp_path), home=home, touched=str(repo / "README.md"))
    assert a.name == "mitzi"  # a file at the top changes nothing

    # Started inside a project folder: named after it from the start.
    b = app.upsert_session("claude_code", "b", cwd=str(repo / "mitzi"), home=str(repo / "mitzi"))
    await wait_until(lambda: b.repo == "projects")
    assert b.name == "mitzi ·b"  # same project as `a` now: told apart by part of the id
    assert b.project == "mitzi"

    # Not told where it started, and first seen deep inside the repo: still the project folder.
    c = app.upsert_session("claude_code", "c", cwd=str(repo / "agent-controller" / "software"))
    await wait_until(lambda: c.name == "agent-controller")
    app.upsert_session("claude_code", "c", cwd=home)
    assert c.name == "agent-controller"
    await app.stop()


async def test_outside_a_repo_the_start_folder_names_the_session(cfg, tmp_path):
    (tmp_path / "scratch" / "deep").mkdir(parents=True)
    app = App(cfg)
    await app.start()
    s = app.upsert_session("claude_code", "s", cwd=str(tmp_path / "scratch"), status="working")
    app.upsert_session("claude_code", "s", cwd=str(tmp_path / "scratch" / "deep"))
    app.upsert_session("claude_code", "s", cwd=str(tmp_path))
    await asyncio.sleep(0.2)
    assert s.name == "scratch"
    await app.stop()
