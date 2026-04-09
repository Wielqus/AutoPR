import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agent.graph import build_graph, AgentState
from integrations.trello import TrelloClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def main() -> None:
    board_id = os.environ["BOARD_ID"]
    trello = TrelloClient()
    graph = build_graph()

    log.info("Fetching AI-labelled Trello cards from board %s", board_id)
    cards = trello.get_ai_cards(board_id)

    if not cards:
        log.info("No AI-labelled cards found. Exiting.")
        return

    cards_sorted = sorted(cards, key=lambda c: c.get("pos", 0))
    log.info("Found %d card(s) to process (ordered by board position):", len(cards_sorted))
    for i, c in enumerate(cards_sorted, 1):
        log.info("  %d. %s", i, c.get("name", ""))

    for card in cards_sorted:
        task_id = card.get("id", "unknown")
        title = card.get("name", "")
        log.info("=" * 60)
        log.info("Processing: %s", title)
        log.info("=" * 60)

        raw_comments = trello.get_card_comments(task_id)
        trello_comments = [
            c["data"]["text"]
            for c in raw_comments
            if c.get("data", {}).get("text")
        ]
        if trello_comments:
            log.info("  Found %d Trello comment(s) for this card", len(trello_comments))

        initial_state: AgentState = {
            "task": card,
            "steps": [],
            "plan_analysis": "",
            "changelog_text": "",
            "task_comments": trello_comments,
            "branch": "",
            "review_report": {},
            "review_iterations": 0,
            "test_iterations": 0,
            "status": "pending",
        }

        try:
            for step_output in graph.stream(initial_state):
                node = next(iter(step_output))
                status = step_output[node].get("status", "")
                log.info(">>> Node finished: %-20s status=%s", node, status)
            pr_url = step_output[node].get("review_report", {}).get("pr_url", "N/A")
            log.info("DONE: %s | PR: %s", title, pr_url)
        except Exception as exc:
            log.error("FAILED: %s | %s", title, exc, exc_info=True)
            log.info("Continuing to next card...")


if __name__ == "__main__":
    main()
