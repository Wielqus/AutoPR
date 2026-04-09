import os

from agent.state import AgentState
from utils.git_utils import get_diff
from utils.claude_cli import run_prompt


def review_code(state: AgentState) -> dict:
    task = state["task"]
    steps = state.get("steps", [])
    plan_text = "\n".join(steps)
    diff = get_diff()

    test_info = state.get("review_report", {})

    diff_limit = 40000
    diff_note = ""
    if len(diff) > diff_limit:
        diff_note = (
            f"NOTE: The diff below is truncated to {diff_limit} characters. "
            f"Do NOT mark a step as missing solely because it is absent from the truncated diff.\n\n"
        )

    project_desc = os.environ.get("PROJECT_DESCRIPTION", "a software project")
    prompt = (
        f"You are a senior code reviewer for {project_desc}. "
        f"The current task is: {task.get('name', '')}.\n"
        f"Review ONLY the diff changes that are directly related to this task. "
        f"IGNORE any changes in the diff that are unrelated to the task — they are noise from a dirty working tree. "
        f"Only flag real problems: incorrect logic, missing required behaviour, or broken tests. "
        f"If a plan step is implemented correctly — even partially visible in the diff — do not flag it. "
        f"When in doubt, PASS — do not block on minor style or speculative issues. "
        f"Always respond in English.\n\n"
        f"{diff_note}"
        f"Implementation plan:\n{plan_text}\n\n"
        f"Git diff (branch changes only):\n{diff[:diff_limit]}\n\n"
        f"Respond in this exact format:\n"
        f"RESULT: PASS or FAIL\n"
        f"ISSUES:\n"
        f"- <issue 1>\n"
        f"(leave ISSUES empty if PASS)\n"
        f"SUMMARY: <one sentence>"
    )

    raw = run_prompt(prompt, timeout=120)

    result = "FAIL"
    issues = []
    summary = ""

    for line in raw.splitlines():
        if line.startswith("RESULT:"):
            result = line.split(":", 1)[1].strip()
        elif line.startswith("- "):
            issues.append(line[2:].strip())
        elif line.startswith("SUMMARY:"):
            summary = line.split(":", 1)[1].strip()

    review_iterations = state.get("review_iterations", 0) + 1

    return {
        "review_report": {
            "result": result,
            "issues": issues,
            "summary": summary,
            "test_passed": test_info.get("test_passed", False),
            "test_output": test_info.get("test_output", ""),
        },
        "review_iterations": review_iterations,
        "status": "reviewed",
    }
