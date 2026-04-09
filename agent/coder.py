import os

from agent.state import AgentState
from utils.git_utils import create_branch, commit_all
from utils.cost_guard import CostGuard
from utils.claude_cli import run_prompt

_cost_guard = CostGuard()


def run_coder(state: AgentState) -> dict:
    task = state["task"]
    task_id = task.get("id", "unknown")
    steps = state.get("steps", [])
    test_iterations = state.get("test_iterations", 0)

    _cost_guard.check_iterations(state)

    branch = state.get("branch", "")
    is_new = True
    if not branch:
        branch, is_new = create_branch(task)

    plan_text = "\n".join(steps)
    task_comments = state.get("task_comments", [])

    comments_section = ""
    if task_comments:
        comments_text = "\n\n".join(task_comments)
        comments_section = (
            f"\n\nTask comments (treat as additional requirements or clarifications):\n{comments_text}"
        )

    project_desc = os.environ.get("PROJECT_DESCRIPTION", "a software project")

    if is_new:
        prompt = (
            f"You are implementing a feature in {project_desc}. "
            f"Create and edit the necessary files to fully implement the feature described below. "
            f"Follow project conventions. Write actual code — do not describe what to do, just do it.\n\n"
            f"Feature: {task.get('name', '')}\n\n"
            f"Implementation steps:\n{plan_text}"
            f"{comments_section}"
        )
    else:
        prompt = (
            f"You are resuming a partially implemented feature in {project_desc}. "
            f"First, review what has already been done on this branch (check git log and the changed files). "
            f"Then:\n"
            f"1. Apply any corrections requested in the task comments below.\n"
            f"2. Implement any steps from the plan that are missing or incomplete.\n"
            f"Do not re-implement steps that are already correctly done. "
            f"Follow project conventions. Write actual code — do not describe what to do, just do it.\n\n"
            f"Feature: {task.get('name', '')}\n\n"
            f"Implementation steps:\n{plan_text}"
            f"{comments_section}"
        )

    repo_dir = os.environ.get("REPO_DIR", ".")
    coder_timeout = int(os.environ.get("CODER_TIMEOUT", "1800"))
    run_prompt(prompt, timeout=coder_timeout, cwd=repo_dir, extra_args=["--dangerously-skip-permissions"])

    commit_all(f"feat: implement {task.get('name', task_id)} (iteration {test_iterations + 1})")

    return {
        "branch": branch,
        "test_iterations": test_iterations + 1,
        "status": "coded",
    }
