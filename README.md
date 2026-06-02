# AIOps Assistant

![Python](https://img.shields.io/badge/python-3.12-blue)
![CI](https://github.com/SeydinaBANE/aiops-assistant/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-multi--stage-2496ED?logo=docker)
![React](https://img.shields.io/badge/react-19-61DAFB?logo=react)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/SeydinaBANE/aiops-assistant)
![GitHub repo size](https://img.shields.io/github/repo-size/SeydinaBANE/aiops-assistant)

Multi-agent incident investigator for IT operations. Automates the detection, investigation, and remediation of infrastructure incidents using LLMs and RAG.

## Architecture

```
                          ┌──────────────┐
                          │  Dashboard   │
                          │ (React SPA)  │
                          │   :80/5173   │
                          └──────┬───────┘
                                 │ HTTP / WS
                                 ▼
Alert (Grafana webhook) ──► FastAPI ──► LangGraph Orchestrator
                                            │
                           ┌─────────────────┼─────────────────┐
                           ▼                 ▼                 ▼
                      Logs Agent     Knowledge Agent    Remediation Agent
                      (Splunk mock)   (RAG on Qdrant)    (LLM playbooks)
                           │                 │                 │
                           └─────────────────┼─────────────────┘
                                             ▼
                                      Incident Report
```

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, data flow, design decisions |
| [docs/api.md](docs/api.md) | Full API reference (endpoints, request/response shapes, errors) |
| [docs/development.md](docs/development.md) | Developer guide (setup, conventions, testing, adding agents) |
| [docs/deployment.md](docs/deployment.md) | Deployment guide (Docker, K8s, Helm, CI/CD, env vars) |
| [AGENTS.md](AGENTS.md) | AI assistant context (commands, conventions, decisions) |
| [DEMO.md](DEMO.md) | 5-minute demo script |
| [TODO.md](TODO.md) | Roadmap and known issues |

## Stack

| Component | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Orchestration | LangGraph |
| LLM | OpenRouter (OpenAI-compatible) |
| Vector Store | Qdrant |
| Embeddings | sentence-transformers |
| Frontend | React 19 + TypeScript |
| Styling | Tailwind CSS v4 |
| Bundler | Vite |
| Proxy | Nginx (production) |
| Container | Docker + Docker Compose |
| K8s | Kind + Helm |
| CI/CD | GitHub Actions → GHCR |
| Observability | OpenTelemetry + Prometheus |

## Quick Start

```bash
# Prerequisites
make setup                          # install python deps + pre-commit hooks
make frontend-install               # install frontend deps

# Copy and fill in your OpenRouter key
cp .env.example .env
# Edit .env → set OPENROUTER_API_KEY

# Run full stack (frontend + api + qdrant + prometheus + otel)
make docker-up

# Seed the knowledge base
uv run scripts/seed_knowledge.py

# Open the dashboard
open http://localhost

# Or simulate an alert via the API
uv run scripts/simulate_alert.py disk-full
```

## API

```bash
# Create incident (triggers investigation)
curl -X POST http://localhost:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{"title":"Disk Space Alert","message":"Disk usage exceeded 90%","severity":"high","labels":{"alertname":"disk-full"}}'

# List incidents
curl http://localhost:8000/incidents

# Get incident details
curl http://localhost:8000/incidents/<id>

# Health check
curl http://localhost:8000/health

# WebSocket streaming (via wscat or the React dashboard)
wscat -c ws://localhost:8000/ws/incidents
# → {"type":"investigating","incident_id":"..."}
# → {"type":"step","step":{...}}
# → {"type":"complete","incident":{...}}
```

## Development

```bash
make check             # lint + format check + type check
make format            # auto-format
make test              # run tests with coverage
make frontend-dev      # Vite dev server with HMR
make ci                # full CI pipeline locally
```

## Deployment

```bash
# Local K8s (Kind)
make kind-create
make helm-install

# Production docker-compose
make docker-up
```

## Project Structure

```
src/                          # Python backend
├── api/                      # REST + WebSocket endpoints
├── agents/                   # Multi-agent system
├── orchestrator/             # LangGraph state machine
├── domain/                   # Core domain models
├── infrastructure/           # Vector store, telemetry, logging
└── services/                 # LLM client
frontend/                     # React SPA
├── src/pages/                # Page components
├── src/components/           # Reusable UI components
├── src/api/                  # API client (HTTP + WS)
└── src/types/                # TypeScript types
tests/                        # pytest suite (coverage ≥ 80%)
scripts/                      # Utility scripts
helm/                         # Kubernetes Helm chart
k8s/                          # Kind cluster config
data/runbooks/                # Mock IT runbooks
```

## Topics

`aiops` · `incident-management` · `langgraph` · `rag` · `fastapi` · `react` · `websocket` · `opentelemetry` · `qdrant` · `docker` · `kubernetes` · `helm`

## License

MIT
