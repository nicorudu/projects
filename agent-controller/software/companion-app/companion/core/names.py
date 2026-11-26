"""What to call a session on screen.

A row shows the session's task title when there is one (a short form of its first prompt).
Otherwise it shows the project. In a git repo that is the top-level folder the session is
working in ("agent-controller"), or the repo name from the git remote when it has only
worked at the top ("projects"). Outside a repo it is the name of the folder it started in.
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


def repo_info(folder: str | None) -> tuple[str, str]:
    """(repo name from the git remote, the repo's top folder) for a folder, or ("", "").

    "projects" for anything inside a clone of github.com/nicorudu/projects, whatever the
    clone's folder is called. Runs git, so call it from a worker thread.
    """
    if not folder or not os.path.isdir(folder):
        return "", ""
    top = _git(folder, "rev-parse", "--show-toplevel")
    repo = repo_from_url(_git(folder, "config", "--get", "remote.origin.url")) if top else ""
    return (repo, os.path.realpath(top)) if repo else ("", "")


def project_folder(repo_top: str, directory: str | None) -> str:
    """The repo's top-level folder that `directory` is in: "agent-controller" for
    <repo>/agent-controller/software. "" at the repo's top, outside it, or in a hidden folder.
    """
    if not repo_top or not directory:
        return ""
    rel = os.path.relpath(os.path.realpath(directory), repo_top)
    first = rel.split(os.sep)[0]
    if first in (".", "..") or first.startswith(".") or os.path.isabs(rel):
        return ""
    return first
