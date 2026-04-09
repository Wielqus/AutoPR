from typing import TypedDict


class AgentState(TypedDict):
    task: dict
    steps: list[str]
    plan_analysis: str
    changelog_text: str
    task_comments: list[str]
    branch: str
    review_report: dict
    review_iterations: int
    test_iterations: int
    status: str
