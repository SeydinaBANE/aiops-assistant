# AIOps Assistant

![Python](https://img.shields.io/badge/python-3.12-blue)
![CI](https://github.com/SeydinaBANE/aiops-assistant/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-multi--stage-2496ED?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/SeydinaBANE/aiops-assistant)
![GitHub repo size](https://img.shields.io/github/repo-size/SeydinaBANE/aiops-assistant)

Multi-agent incident investigator for IT operations. Automates the detection, investigation, and remediation of infrastructure incidents using LLMs and RAG.

## Architecture

```
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

## Stack

| Component | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Orchestration | LangGraph |
| LLM | OpenRouter (OpenAI-compatible) |
| Vector Store | Qdrant |
| Embeddings | sentence-transformers |
| Container | Docker + Docker Compose |
| K8s | Kind + Helm |
| CI/CD | GitHub Actions → GHCR |
| Observability | OpenTelemetry + Prometheus |

## Quick Start

```bash
# Prerequisites
make setup                          # install deps + pre-commit hooks

# Copy and fill in your OpenRouter key
cp .env.example .env
# Edit .env → set OPENROUTER_API_KEY

# Run full stack
make docker-up                      # api + qdrant + prometheus + otel

# Seed the knowledge base
uv run scripts/seed_knowledge.py

# Simulate an alert
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
```

## Development

```bash
make check      # lint + format check + type check
make format     # auto-format
make test       # run tests with coverage
make ci         # full CI pipeline locally
```

## Deployment

```bash
# Local K8s (Kind)
make kind-create
make helm-install

# Production image
make docker-build
docker tag aiops-assistant ghcr.io/<your-org>/aiops-assistant:latest
docker push ghcr.io/<your-org>/aiops-assistant:latest
```

## Project Structure

```
src/                          # Application code
├── api/                      # REST endpoints
├── agents/                   # Multi-agent system
├── orchestrator/             # LangGraph state machine
├── domain/                   # Core domain models
├── infrastructure/           # Vector store, telemetry, logging
└── services/                 # LLM client
tests/                        # pytest suite (coverage ≥ 80%)
scripts/                      # Utility scripts
helm/                         # Kubernetes Helm chart
k8s/                          # Kind cluster config
data/runbooks/                # Mock IT runbooks
```

## Topics

`aiops` · `incident-management` · `langgraph` · `rag` · `fastapi` · `opentelemetry` · `qdrant` · `docker` · `kubernetes` · `helm`

## License

MIT
