import os
import logging

from agent.state import AgentState
from utils.git_utils import push_branch
from utils.claude_cli import run_prompt

log = logging.getLogger(__name__)


def _get_pr_client():
    if os.environ.get("GH_TOKEN"):
        from integrations.github import GitHubClient
        return GitHubClient()
    from integrations.bitbucket import BitbucketClient
    return BitbucketClient()


def _get_trello_client():
    if os.environ.get("TRELLO_API_KEY"):
        from integrations.trello import TrelloClient
        return TrelloClient()
    return None


def _generate_test_instructions(task: dict, review_report: dict) -> str:
    project_desc = os.environ.get("PROJECT_DESCRIPTION", "a software project")
    prompt = (
        f"Based on this feature for {project_desc}, write 3-5 short bullet points "
        f"on how to manually test the change. "
        f"Be specific and practical. Always write in English.\n\n"
        f"Feature: {task.get('name', '')}\n"
        f"Description: {task.get('desc', '')[:500]}\n"
        f"Review summary: {review_report.get('summary', '')}\n\n"
        f"Return only the bullet points, nothing else."
    )
    return run_prompt(prompt)


def create_pull_request(state: AgentState) -> dict:
    task = state["task"]
    task_id = task.get("id", "unknown")
    title = task.get("name", "")
    url = task.get("url", "")
    branch = state.get("branch", f"ai/{task_id}")
    review_report = state.get("review_report", {})
    plan_analysis = state.get("plan_analysis", "")
    changelog_text = state.get("changelog_text", "")

    task_link = f"**Task:** {url}\n\n" if url else ""
    description = (
        f"## AI Implementation\n\n"
        f"{task_link}"
        f"**Review summary:** {review_report.get('summary', 'N/A')}\n\n"
        f"### Task Analysis\n\n"
        f"{plan_analysis}\n\n"
        f"---\n\n"
        f"{changelog_text}"
    )

    push_branch(branch)

    pr_client = _get_pr_client()
    pr_url = pr_client.create_pull_request(
        title=f"AI: {title}",
        description=description,
        branch=branch,
    )

    test_instructions = _generate_test_instructions(task, review_report)

    trello = _get_trello_client()
    if trello:
        trello_comment = (
            f"PR opened: {pr_url}\n\n"
            f"*How to test:*\n{test_instructions}"
        )
        trello.update_card_status(task_id, trello_comment)

        review_list_id = os.environ.get("TRELLO_REVIEW_LIST_ID")
        if review_list_id:
            trello.move_card_to_list(task_id, review_list_id)
    else:
        log.info("PR opened: %s", pr_url)

    return {
        "status": "pr_opened",
        "review_report": {
            **review_report,
            "pr_url": pr_url,
        },
    }
