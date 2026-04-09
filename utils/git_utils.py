import os
import git

from utils.slug import task_slug


def _repo() -> git.Repo:
    repo_dir = os.environ.get("REPO_DIR", ".")
    return git.Repo(repo_dir)


def create_branch(task: dict) -> tuple[str, bool]:
    """Return (branch_name, is_new). If branch already exists, check it out instead."""
    branch_name = task_slug(task)
    repo = _repo()
    try:
        repo.git.stash("--include-untracked")
    except git.GitCommandError:
        pass
    try:
        base = os.environ.get("BASE_BRANCH", "main")
        repo.git.checkout(base)
        repo.git.checkout("-b", branch_name)
        return branch_name, True
    except git.GitCommandError:
        # Branch already exists locally — just switch to it
        repo.git.checkout(branch_name)
        return branch_name, False


def commit_all(message: str) -> None:
    repo = _repo()
    repo.git.add("-A")
    author_name = os.environ.get("GIT_AUTHOR_NAME", "AI Agent")
    author_email = os.environ.get("GIT_AUTHOR_EMAIL", "ai-agent@noreply.local")
    actor = git.Actor(author_name, author_email)
    repo.index.commit(message, author=actor, committer=actor)


def push_branch(branch_name: str) -> None:
    repo = _repo()
    repo.git.push("origin", branch_name, set_upstream=True)


def get_diff(base: str = "") -> str:
    if not base:
        base = os.environ.get("BASE_BRANCH", "main")
    repo = _repo()
    try:
        return repo.git.diff(f"{base}...HEAD")
    except git.GitCommandError:
        return repo.git.diff("HEAD")
