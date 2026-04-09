import os

from agent.state import AgentState
from utils.git_utils import commit_all, get_diff
from utils.cost_guard import CostGuard
from utils.claude_cli import run_prompt

_cost_guard = CostGuard()


def fix_issues(state: AgentState) -> dict:
    _cost_guard.check_iterations(state)

    report = state.get("review_report", {})
    issues = report.get("issues", [])

    test_output = state.get("review_report", {}).get("test_output", "")
    test_passed = state.get("review_report", {}).get("test_passed", True)

    issues_text = "\n".join(f"- {issue}" for issue in issues) if issues else ""
    diff = get_diff()

    project_desc = os.environ.get("PROJECT_DESCRIPTION", "a software project")
    task = state["task"]
    prompt_parts = [
        f"Fix specific issues in {project_desc}. Task: {task.get('name', '')}.\n"
        f"IMPORTANT: only fix issues related to this task. Only edit files listed in the diff below. "
        f"Do NOT touch anything outside the task scope.\n\n"
        f"Branch diff (the only files you should touch):\n{diff[:20000]}"
    ]
    if not test_passed and test_output:
        prompt_parts.append(f"\nFailing tests output:\n{test_output[-3000:]}\nFix the code and/or tests so all tests pass.")
    if issues_text:
        prompt_parts.append(f"\nCode review issues to fix:\n{issues_text}")

    prompt = "\n".join(prompt_parts)

    repo_dir = os.environ.get("REPO_DIR", ".")
    coder_timeout = int(os.environ.get("CODER_TIMEOUT", "1800"))
    run_prompt(prompt, timeout=coder_timeout, cwd=repo_dir, extra_args=["--dangerously-skip-permissions"])

    review_iterations = state.get("review_iterations", 0)
    commit_all(f"fix: address review issues (round {review_iterations})")

    return {"status": "fixed"}
