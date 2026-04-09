# LouerAgent

Autonomous AI development agent that turns Trello cards into pull requests. Powered by Claude and orchestrated with LangGraph.

## How it works

The agent picks up Trello cards labelled **"AI"** and runs them through a full development pipeline — from planning to PR creation — without human intervention.

```
Trello card
    |
    v
 Planner ---- generates implementation steps using Claude
    |
    v
  Coder ----- writes code via Claude Code CLI, commits to a new branch
    |
    v
  Tester ---- runs your test suite
    |    \
    |     v
    |   Fixer -- sends failures back to Claude for targeted fixes (up to 3 rounds)
    |     |
    |     +----> back to Tester
    v
 Reviewer --- Claude reviews the diff against the plan
    |    \
    |     v
    |   Fixer -- fixes review issues (up to 3 rounds)
    |     |
    |     +----> back to Tester
    v
 Changelog -- generates a changelog from the diff
    |
    v
 Pull Request - opens a PR (GitHub or Bitbucket), posts status to Trello
```

Each card goes through: **plan -> code -> test -> review -> fix (loop) -> changelog -> PR**.

Safety guards prevent runaway costs: max 5 test iterations and max 3 review loops.

## Project structure

```
ai-dev-agent/
  worker.py              # Entry point — fetches Trello cards and runs the pipeline
  agent/
    graph.py             # LangGraph workflow definition
    state.py             # Shared state (TypedDict)
    planner.py           # Generates implementation plan
    coder.py             # Writes code via Claude Code CLI
    tester.py            # Runs test suite
    reviewer.py          # AI code review (PASS/FAIL)
    fixer.py             # Fixes test failures and review issues
    changelog.py         # Generates changelog from diff
    pull_request.py      # Creates PR, updates Trello
  integrations/
    github.py            # GitHub PR client
    bitbucket.py         # Bitbucket PR client
    trello.py            # Trello API client
  utils/
    claude_cli.py        # Claude Code CLI wrapper
    git_utils.py         # Branch, commit, diff helpers
    cost_guard.py        # Iteration limits to prevent runaway costs
    slug.py              # Branch name generation from task title
```

## Requirements

- Python 3.10+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and in `$PATH`
- Trello board with **"AI"** label on cards to process
- GitHub or Bitbucket account for pull requests

## Setup

```bash
cd ai-dev-agent
pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
```

## Configuration

All configuration is done via environment variables (`.env` file). See `.env.example` for all options.

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key |
| `REPO_DIR` | Yes | Absolute path to the target git repository |
| `TEST_CMD` | Yes | Command to run tests (`pytest`, `npm test`, `php artisan test`, etc.) |
| `PROJECT_DESCRIPTION` | No | One-line project description (improves LLM prompts) |
| `BASE_BRANCH` | No | Base branch for PRs (default: `main`) |
| `TRELLO_API_KEY` | Yes | Trello API key |
| `TRELLO_TOKEN` | Yes | Trello token |
| `BOARD_ID` | Yes | Trello board ID |
| `GH_TOKEN` | * | GitHub personal access token |
| `GH_REPO` | * | GitHub repo (`owner/repo`) |
| `BB_USER` / `BB_TOKEN` | * | Bitbucket credentials |
| `WORKSPACE` / `REPO` | * | Bitbucket workspace and repo slug |
| `CLAUDE_CODE_MODEL` | No | Claude model to use (default: `claude-sonnet-4-6`) |
| `CODER_TIMEOUT` | No | Max seconds for code generation (default: `1800`) |

\* Set either GitHub **or** Bitbucket credentials.

## Usage

```bash
python worker.py
```

The agent will:
1. Fetch all Trello cards with the **"AI"** label
2. Process each card through the full pipeline (ordered by board position)
3. Open a PR and comment the link + test instructions on the Trello card
4. Move the card to the review list (if `TRELLO_REVIEW_LIST_ID` is set)

Works with **any** language or framework — just set `TEST_CMD` and `PROJECT_DESCRIPTION` to match your stack.
