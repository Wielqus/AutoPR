import os
import logging

from agent.state import AgentState
from utils.git_utils import get_diff
from utils.claude_cli import run_prompt

log = logging.getLogger(__name__)

DEFAULT_DOC_PROMPT = """You are a documentation maintainer for a software project.

## Your task

You will receive a `git diff` of source files. Analyse the diff and update any project
documentation files that need to reflect the changes in business logic or behaviour.

## Rules

- Make minimal, precise edits — only update sections affected by the diff.
- Do not duplicate information across documents — cross-link instead.
- If nothing requires updating, print: `No documentation changes needed.`
- After all edits, print a one-line summary per changed file:
  `Updated: <path> — <what changed>`
"""


def _load_doc_prompt() -> str:
    prompt_file = os.environ.get("DOC_UPDATE_PROMPT_FILE")
    if prompt_file and os.path.isfile(prompt_file):
        with open(prompt_file, "r") as f:
            return f.read()
    return DEFAULT_DOC_PROMPT


def update_docs(state: AgentState) -> dict:
    repo_dir = os.environ.get("REPO_DIR", ".")

    if not os.environ.get("DOC_UPDATE_ENABLED", "").lower() in ("1", "true", "yes"):
        log.info("Doc updater disabled (set DOC_UPDATE_ENABLED=1 to enable)")
        return {"status": "docs_skipped"}

    diff = get_diff(base="main")
    if not diff.strip():
        return {"status": "docs_updated"}

    system_prompt = _load_doc_prompt()

    prompt = (
        f"{system_prompt}\n\n"
        f"## Git diff\n\n"
        f"```diff\n{diff[:12000]}\n```\n\n"
        f"Update any relevant documentation in the repository at: {repo_dir}"
    )

    run_prompt(prompt, timeout=600, cwd=repo_dir, extra_args=["--dangerously-skip-permissions"])

    return {"status": "docs_updated"}
