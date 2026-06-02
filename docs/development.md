# Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js 22+ (for frontend)
- Docker Desktop (for Qdrant, Prometheus, OTEL collector)
- OpenRouter API key (free tier works)

## Setup

```bash
make setup                # Python deps + pre-commit hooks
make frontend-install     # Frontend deps (npm ci)
```

Backend setup runs `uv sync --extra dev` (installs all dependencies including dev tools) and `pre-commit install` (hooks for ruff, mypy, bandit, etc.).

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

### Full stack (production-like)

```bash
make docker-up
```

Starts five containers:
- **frontend** (nginx, port 80) — serves React SPA, proxies `/api` and `/ws` to the API
- **api** (hot-reloads on source changes via volume mount)
- **qdrant** (vector store, port 6333)
- **otel-collector** (tracing, port 4318)
- **prometheus** (metrics, port 9090)

Open http://localhost in your browser.

### Frontend development (hot reload)

```bash
# Terminal 1: start the backend + dependencies
make docker-up

# Terminal 2: start Vite dev server
make frontend-dev
```

Vite proxies `/api` and `/ws` to `localhost:8000` with hot module replacement. Open http://localhost:5173.

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

Frontend type checking is done via `cd frontend && npx tsc --noEmit` and the build step (`npm run build`) includes type checking.

## Project conventions

### Backend (Python)

- **Python 3.12+ syntax**: `str | None`, `TypeVar`, `Protocol`
- **Strict typing**: mypy `--strict` on all source files. No `Any`, `dict`, or `list` without type parameters.
- **No comments**: code must be self-documenting. Use descriptive names and small functions.
- **`from __future__ import annotations`**: every type-annotated file.
- **No `print`**: use `structlog.get_logger()` for logging.
- **Testing**: one nominal + one edge-case test per function. Mock the LLM layer.

### Frontend (TypeScript/React)

- **Strict TypeScript**: `strict: true` in tsconfig — no `any`, no implicit returns.
- **No unused imports/vars**: `noUnusedLocals`, `noUnusedParameters` are errors.
- **Tailwind CSS**: utility classes only — no custom CSS files (single `index.css` imports Tailwind).
- **React 19**: functional components + hooks. No class components.
- **Type safety**: all API responses typed via `types/incident.ts` (mirrors Pydantic models).

## Project layout

```
src/                          # Python backend
├── api/routes.py             # FastAPI endpoints (REST)
├── api/websocket.py          # FastAPI endpoint (WebSocket)
├── api/schemas.py            # Pydantic models
├── agents/protocol.py        # Agent Protocol
├── agents/logs_agent.py      # 3 agent implementations
├── orchestrator/graph.py     # LangGraph pipeline
├── orchestrator/state.py     # TypedDict state
├── domain/incident.py        # Domain models
├── infrastructure/           # Qdrant, telemetry, logging
├── services/llm.py           # OpenRouter client
├── config.py                 # Settings
└── main.py                   # App entry point
frontend/                     # React SPA
├── src/pages/                # NewInvestigation, IncidentsList, IncidentDetail
├── src/components/           # Layout, IncidentCard, StepTimeline
├── src/api/                  # REST + WebSocket client
├── src/types/                # TypeScript types
└── vite.config.ts            # Dev proxy to localhost:8000
```

## Testing patterns

### Mocking the LLM

The `conftest.py` fixture `mock_llm` patches `src.agents.logs_agent.ask_llm` to return `"Mocked LLM response."`. All agent tests use this — no real API calls.

### Mocking the vector store

The `mock_vector_store` fixture patches `src.api.routes._vector_store` with a `MagicMock` that returns a single runbook result. Tests don't need Qdrant running.

### Mocking the WebSocket investigation

The `tests/test_api/test_websocket.py` patches `src.api.websocket.run_investigation` and uses `TestClient.websocket_connect` to test the streaming flow:

```python
@patch("src.api.websocket.run_investigation")
def test_ws_investigation_streams_steps(self, mock_investigation, client):
    with client.websocket_connect("/ws/incidents") as ws:
        ws.send_json(payload)
        investigating = ws.receive_json()
        assert investigating["type"] == "investigating"
        complete = ws.receive_json()
        assert complete["type"] == "complete"
```

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
3. Register it in `src/api/routes.py` and `src/api/websocket.py`
4. Add a test file in `tests/test_agents/`
5. Seed relevant runbooks in `data/runbooks/`

## Adding a new runbook

Create a markdown file in `data/runbooks/` following the existing format with sections: Symptoms, Investigation, Remediation, Prevention. Then re-run `scripts/seed_knowledge.py`.

## Adding a new frontend page

1. Create the page component in `frontend/src/pages/`
2. Add a route in `frontend/src/App.tsx`
3. If it needs API calls, add functions to `frontend/src/api/client.ts`
4. Add types to `frontend/src/types/incident.ts` if needed
