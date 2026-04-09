import os

from agent.state import AgentState
from utils.filesystem import ensure_dir, write_file
from utils.slug import task_slug
from utils.claude_cli import run_prompt


def generate_documentation(state: AgentState) -> dict:
    task = state["task"]
    title = task.get("name", "")
    description = task.get("desc", "")
    url = task.get("url", "")
    steps = state.get("steps", [])

    repo_dir = os.environ.get("REPO_DIR", ".")
    slug = task_slug(task)
    doc_file = os.path.join(repo_dir, "docs", f"{slug}.md")
    ensure_dir(os.path.dirname(doc_file))

    plan_text = "\n".join(steps)
    prompt = (
        f"Generate a short single Markdown document for a Laravel feature implementation. "
        f"Always write in English. Include these sections: "
        f"Overview, Trello link, Implementation plan (numbered), How to test the change. "
        f"Keep it concise and to the point.\n\n"
        f"Title: {title}\n"
        f"Trello link: {url}\n"
        f"Description: {description}\n"
        f"Implementation plan:\n{plan_text}\n\n"
        f"Return only the Markdown document, nothing else."
    )

    content = run_prompt(prompt)
    write_file(doc_file, content)

    return {
        "docs_path": doc_file,
        "status": "documented",
    }
