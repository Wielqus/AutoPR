import os

from agent.state import AgentState
from utils.claude_cli import run_prompt


def plan_task(state: AgentState) -> dict:
    task = state["task"]
    title = task.get("name", "")
    description = task.get("desc", "")
    repo_dir = os.environ.get("REPO_DIR", ".")

    project_desc = os.environ.get("PROJECT_DESCRIPTION", "a software project")
    steps_prompt = (
        f"You are a senior software engineer working on {project_desc}. "
        f"Given the following task, produce a numbered list of concrete implementation steps. "
        f"Be specific and actionable. Always respond in English.\n\n"
        f"Task title: {title}\n"
        f"Description: {description}\n\n"
        f"Return only the numbered list, nothing else."
    )

    raw = run_prompt(steps_prompt, timeout=120)
    steps = [line.strip() for line in raw.splitlines() if line.strip()]

    analysis_prompt = (
        f"You are a senior software engineer working on {project_desc}. "
        f"Analyse the following task and write a brief technical summary covering: "
        f"what the change achieves, which parts of the system are affected, and any risks or edge cases. "
        f"Always write in English. Be concise (max 8 sentences).\n\n"
        f"Task title: {title}\n"
        f"Description: {description}\n"
        f"Implementation steps:\n" + "\n".join(steps) + "\n\n"
        f"Return only the analysis text, nothing else."
    )

    plan_analysis = run_prompt(analysis_prompt, timeout=120)

    return {
        "steps": steps,
        "plan_analysis": plan_analysis,
        "status": "planned",
    }
