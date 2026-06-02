# AGENTS.md — AIOps Assistant

## Commands

```bash
make setup              # Python deps + pre-commit hooks
make frontend-install   # Frontend deps (npm ci)
make check              # Lint + format check + type check
make format             # Auto-format
make test               # Tests with coverage
make frontend-dev       # Vite dev server (HMR on :5173, proxies :8000)
make frontend-build     # Production build
make docker-up          # Start full stack (frontend + api + qdrant + otel + prom)
make ci                 # Full local CI
```

## Conventions

### Backend (Python)

- **Python 3.12+** — use `str | None` syntax, `TypeVar`, `Protocol`
- **Type hints** — strict mypy everywhere (`--strict`)
- **No comments in code** — code must be self-documenting
- **No `Any`, `dict`, `list`** without concrete type params
- **Tests** — one nominal + one edge case per function; coverage ≥ 80%
- **Imports** — `from __future__ import annotations` in every file with type hints
- **Logging** — use `structlog`, never `print`
- **API** — always return Pydantic models, never raw dicts
- **LLM** — always mock in unit tests

### Frontend (TypeScript/React)

- **Strict TypeScript** — `strict: true`, no `any`, no implicit returns
- **No unused imports/vars** — `noUnusedLocals`, `noUnusedParameters` are errors
- **Tailwind CSS** — utility classes only, no custom CSS
- **React 19** — functional components + hooks only
- **Types mirror Pydantic** — `frontend/src/types/incident.ts` matches backend models

## Decisions

- OpenRouter for model flexibility (switch model via env var)
- Qdrant for vector store (lightweight, Docker, gRPC support)
- LangGraph for agent orchestration (state machine, not DAG)
- uv over pip (faster, lockfile, workspace support)
- ruff over flake8/black/isort (single tool, faster)
- mypy strict over pyright (stricter defaults)
- distroless Docker image over slim (smaller attack surface)
- Vite + React over Next.js (simpler SPA, no SSR needed)
- Tailwind v4 over CSS modules (utility-first, zero-runtime)
- WebSocket callbacks over LangGraph streaming (simpler to test)

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design
- [docs/api.md](docs/api.md) — API reference
- [docs/development.md](docs/development.md) — developer how-to
- [docs/deployment.md](docs/deployment.md) — deployment how-to

## Session notes

Create the project at `/Users/baneseydina/Desktop/app/aiops-assistant`.

- WebSocket handler in `src/api/websocket.py` imports `_incidents` and `_to_response` from `routes.py`
- `AgentNode` and `run_investigation` accept optional `step_callback` for streaming
- Frontend dev mode: Vite on :5173 proxies `/api` and `/ws` to :8000
- Frontend prod mode: nginx on :80 serves SPA + reverse proxy to api:8000

## Remote (GitHub)

- Repo: `ghcr.io/seydinabane/aiops-assistant`
- CI runs on push/PR to main (quality → test → frontend → build → push GHCR)
- Docker image pushed to GHCR on main merge
