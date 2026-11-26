"""What to call a session on screen.

A row shows the session's task title when there is one (a short form of its first prompt).
Otherwise it shows the project: the repo name from the git remote, then the folder name.
"""

from __future__ import annotations

import os
import re
import subprocess

TITLE_MAX = 60


def short_title(prompt: str | None) -> str:
    """A one-line title from a prompt, or "" if the prompt can't serve as one."""
    text = (prompt or "").strip()
    if not text or text.startswith("/"):  # slash commands (/clear, /model) aren't tasks
        return ""
    first_line = re.sub(r"\s+", " ", text.splitlines()[0]).strip()
    if len(first_line) <= TITLE_MAX:
        return first_line
    cut = first_line[:TITLE_MAX].rsplit(" ", 1)[0] or first_line[:TITLE_MAX]
    return cut.rstrip(" ,;:.") + "…"


def repo_from_url(url: str | None) -> str:
    """"projects" from https://github.com/nicorudu/projects.git or git@github.com:nicorudu/projects.git."""
    name = re.split(r"[/:]", (url or "").strip().rstrip("/"))[-1]
    return name[:-4] if name.endswith(".git") else name


def _git(cwd: str, *args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=3)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def repo_label(cwd: str | None) -> str:
    """The project name for a folder, from its git remote. "" if it has none.

    At the repo's top folder this is the repo name ("projects"). Further in, the folder is
    added ("projects/mitzi"), so two sessions in one repo can be told apart.
    Runs git, so call it from a worker thread.
    """
    if not cwd or not os.path.isdir(cwd):
        return ""
    top = _git(cwd, "rev-parse", "--show-toplevel")
    repo = repo_from_url(_git(cwd, "config", "--get", "remote.origin.url")) if top else ""
    if not repo:
        return ""
    rel = os.path.relpath(os.path.realpath(cwd), os.path.realpath(top))
    return repo if rel == "." else f"{repo}/{os.path.basename(rel)}"
