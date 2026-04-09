import os

from agent.state import AgentState
from utils.git_utils import get_diff
from utils.claude_cli import run_prompt


def generate_changelog(state: AgentState) -> dict:
    task = state["task"]
    title = task.get("name", "")

    base = os.environ.get("BASE_BRANCH", "main")
    diff = get_diff(base=base)

    prompt = (
        f"Generate a short changelog section for the following git diff. Always write in English.\n\n"
        f"Task: {title}\n\n"
        f"Git diff (main..HEAD):\n{diff[:8000]}\n\n"
        f"Format as Markdown: ## Changelog, then bullet points: files modified and what changed. "
        f"Max 10 lines. Be concise and factual."
    )

    changelog_text = run_prompt(prompt)

    return {
        "changelog_text": changelog_text,
        "status": "changelog_generated",
    }
