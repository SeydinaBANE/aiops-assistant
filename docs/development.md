# Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker Desktop (for Qdrant, Prometheus, OTEL collector)
- OpenRouter API key (free tier works)

## Setup

```bash
make setup
```

This runs `uv sync --extra dev` (installs all dependencies including dev tools) and `pre-commit install` (hooks for ruff, mypy, bandit, etc.).

## Environment

```bash
cp .env.example .env
```

Edit `.env` to set `OPENROUTER_API_KEY`. All other variables have sensible defaults for local development.

```env
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=openai/gpt-4o-mini
LLM_MAX_TOKENS=4096
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Running the stack

```bash
make docker-up
```

Starts four containers:
- **api** (hot-reloads on source changes via volume mount)
- **qdrant** (vector store, port 6333)
- **otel-collector** (tracing, port 4318)
- **prometheus** (metrics, port 9090)

First-time setup takes ~30s for Qdrant to initialize. Check `make docker-logs` if the API fails to connect.

## Seed data

```bash
uv run scripts/seed_knowledge.py
```

This loads the three runbooks from `data/runbooks/` into Qdrant. Required for the KnowledgeAgent to return relevant results.

## Simulate an alert

```bash
uv run scripts/simulate_alert.py disk-full
uv run scripts/simulate_alert.py high-cpu
uv run scripts/simulate_alert.py service-down --url http://localhost:8000
```

Each creates an incident and runs the full investigation pipeline. The response includes the incident ID.

## Code quality

```bash
make check      # ruff lint + ruff format check + mypy strict
make format     # auto-fix all formatting
make test       # pytest with coverage (threshold: 80%)
make ci         # full pipeline (check + test)
```

All checks must pass before committing. The pre-commit hooks enforce this automatically.

## Project conventions

- **Python 3.12+ syntax**: `str | None`, `TypeVar`, `Protocol`
- **Strict typing**: mypy `--strict` on all source files. No `Any`, `dict`, or `list` without type parameters.
- **No comments**: code must be self-documenting. Use descriptive names and small functions.
- **`from __future__ import annotations`**: every type-annotated file.
- **No `print`**: use `structlog.get_logger()` for logging.
- **Testing**: one nominal + one edge-case test per function. Mock the LLM layer.
- **Structure**: one function, one responsibility (max ~30 lines).

## Project layout

```
src/
├── api/routes.py          # FastAPI endpoints
├── api/schemas.py         # Pydantic models
├── agents/protocol.py     # Agent Protocol
├── agents/logs_agent.py   # 3 agent implementations
├── orchestrator/graph.py  # LangGraph pipeline
├── orchestrator/state.py  # TypedDict state
├── domain/incident.py     # Domain models
├── infrastructure/        # Qdrant, telemetry, logging
├── services/llm.py        # OpenRouter client
├── config.py              # Settings
└── main.py                # App entry point
```

## Testing patterns

### Mocking the LLM

The `conftest.py` fixture `mock_llm` patches `src.agents.logs_agent.ask_llm` to return `"Mocked LLM response."`. All agent tests use this — no real API calls.

### Mocking the vector store

The `mock_vector_store` fixture patches `src.api.routes._vector_store` with a `MagicMock` that returns a single runbook result. Tests don't need Qdrant running.

### Writing new tests

```python
async def test_my_feature_normal_case(mock_llm, sample_incident):
    agent = MyAgent()
    result = await agent.investigate(sample_incident)
    assert result.status == "success"

async def test_my_feature_edge_case(mock_llm, sample_incident):
    agent = MyAgent()
    # mutate incident for edge case
    result = await agent.investigate(sample_incident)
    assert result.status == "error"
```

## Adding a new agent

1. Add the agent class in `src/agents/logs_agent.py` implementing the `Agent` protocol
2. Add the node to `src/orchestrator/graph.py` in `build_graph()`
3. Add a test file in `tests/test_agents/`
4. Seed relevant runbooks in `data/runbooks/`

## Adding a new runbook

Create a markdown file in `data/runbooks/` following the existing format with sections: Symptoms, Investigation, Remediation, Prevention. Then re-run `scripts/seed_knowledge.py`.
