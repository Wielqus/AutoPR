import os

from agent.state import AgentState
from utils.claude_cli import run_prompt


def load_docs(state: AgentState) -> dict:
    task = state["task"]
    title = task.get("name", "")
    description = task.get("desc", "")
    repo_dir = os.environ.get("REPO_DIR", ".")

    prompt = (
        f"Read docs/ai/index.md, then read all nodes that are relevant to the following task. "
        f"Output the full content of each relevant node, one after another, with a header showing the file path. "
        f"Do not summarise — output the raw node content so it can be used as context by other agents.\n\n"
        f"Task: {title}\n"
        f"Description: {description}"
    )

    docs_context = run_prompt(prompt, timeout=300, cwd=repo_dir)

    return {
        "docs_context": docs_context,
        "status": "docs_loaded",
    }
