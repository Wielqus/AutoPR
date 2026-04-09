from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.planner import plan_task
from agent.coder import run_coder
from agent.tester import run_tests
from agent.reviewer import review_code
from agent.fixer import fix_issues
from agent.changelog import generate_changelog
from agent.pull_request import create_pull_request


def _route_tester(state: AgentState) -> str:
    report = state.get("review_report", {})
    test_iterations = state.get("test_iterations", 0)
    if not report.get("test_passed", False) and test_iterations < 3:
        return "fixer"
    return "reviewer"


def _route_reviewer(state: AgentState) -> str:
    report = state.get("review_report", {})
    iterations = state.get("review_iterations", 0)
    if report.get("result") == "FAIL" and iterations < 3:
        return "fixer"
    return "changelog"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner", plan_task)
    graph.add_node("coder", run_coder)
    graph.add_node("tester", run_tests)
    graph.add_node("reviewer", review_code)
    graph.add_node("fixer", fix_issues)
    graph.add_node("changelog", generate_changelog)
    graph.add_node("pull_request", create_pull_request)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "tester")
    graph.add_conditional_edges(
        "tester",
        _route_tester,
        {"fixer": "fixer", "reviewer": "reviewer"},
    )
    graph.add_conditional_edges(
        "reviewer",
        _route_reviewer,
        {"fixer": "fixer", "changelog": "changelog"},
    )
    graph.add_edge("fixer", "tester")
    graph.add_edge("changelog", "pull_request")
    graph.add_edge("pull_request", END)

    return graph.compile()
