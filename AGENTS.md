# AGENTS.md — AIOps Assistant

## Commands

```bash
make setup       # First time setup
make check       # Lint + format check + type check
make format      # Auto-format
make test        # Tests with coverage
make ci          # Full local CI
make docker-up   # Start full stack
```

## Conventions

- **Python 3.12+** — use `str | None` syntax, `TypeVar`, `Protocol`
- **Type hints** — strict mypy everywhere (`--strict`)
- **No comments in code** — code must be self-documenting
- **No `Any`, `dict`, `list`** without concrete type params
- **Tests** — one nominal + one edge case per function; coverage ≥ 80%
- **Imports** — `from __future__ import annotations` in every file with type hints
- **Logging** — use `structlog`, never `print`
- **API** — always return Pydantic models, never raw dicts
- **LLM** — always mock in unit tests

## Decisions

- OpenRouter for model flexibility (switch model via env var)
- Qdrant for vector store (lightweight, Docker, gRPC support)
- LangGraph for agent orchestration (state machine, not DAG)
- uv over pip (faster, lockfile, workspace support)
- ruff over flake8/black/isort (single tool, faster)
- mypy strict over pyright (stricter defaults)
- distroless Docker image over slim (smaller attack surface)

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design
- [docs/api.md](docs/api.md) — API reference
- [docs/development.md](docs/development.md) — developer how-to
- [docs/deployment.md](docs/deployment.md) — deployment how-to

## Session notes

Create the project at `/Users/baneseydina/Desktop/app/aiops-assistant`.

## Remote (GitHub)

- Repo: `ghcr.io/baneseydina/aiops-assistant`
- CI runs on push/PR to main
- Docker image pushed to GHCR on main merge
