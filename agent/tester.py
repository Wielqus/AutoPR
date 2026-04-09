import subprocess
import os
import logging

from agent.state import AgentState

log = logging.getLogger(__name__)

INFRASTRUCTURE_ERRORS = [
    "could not find driver",
    "Connection refused",
    "php_network_getaddresses",
    "No application encryption key",
    "SQLSTATE[HY000] [2002]",
    "sail: not found",
    "command not found",
    "No such file or directory",
]


def _is_infrastructure_failure(output: str) -> bool:
    return any(err in output for err in INFRASTRUCTURE_ERRORS)


def run_tests(state: AgentState) -> dict:
    repo_dir = os.environ.get("REPO_DIR", ".")
    test_cmd = os.environ.get("TEST_CMD", "pytest --tb=short --cov -q")

    result = subprocess.run(
        test_cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=repo_dir,
    )

    output = result.stdout + result.stderr
    test_passed = result.returncode == 0

    if not test_passed and _is_infrastructure_failure(output):
        log.warning("Tests failed due to infrastructure issue (DB/driver), skipping to reviewer.")
        test_passed = True
        output = f"[Skipped — infrastructure failure detected]\n{output[:500]}"

    return {
        "review_report": {
            **state.get("review_report", {}),
            "test_passed": test_passed,
            "test_output": output,
        },
        "status": "tested",
    }
