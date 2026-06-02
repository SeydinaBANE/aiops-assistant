# Deployment Guide

## Local development (Docker Compose)

```bash
make docker-up        # Build and start all services
make docker-logs      # Tail logs
make docker-down      # Stop everything
```

The stack includes:

| Service | Image | Port | Role |
|---|---|---|---|
| **frontend** | nginx:alpine | `80` | Serves React SPA, proxies `/api` and `/ws` to the API |
| **api** | Build from Dockerfile | `8000` | FastAPI application (auto-reloads on source changes) |
| **qdrant** | qdrant/qdrant:v1.13 | `6333` | Vector store for RAG |
| **otel-collector** | otel/opentelemetry-collector-contrib | `4318` | Trace collection |
| **prometheus** | prom/prometheus:v3.2 | `9090` | Metrics storage |

Open http://localhost in your browser to access the React dashboard.

## Production images

### Backend

```bash
make docker-build
```

Builds a multi-stage Docker image:

| Stage | Base | Purpose |
|---|---|---|
| `builder` | `python:3.12-slim` | Install deps via uv, compile bytecode |
| runtime | `python:3.12-slim` | Copy `.venv` + `src/`, set non-root user |

The image runs as `appuser` (UID 1000) with `PYTHONUNBUFFERED=1` and a healthcheck on `/health`.

### Frontend

```bash
cd frontend && docker build -t aiops-assistant-frontend:latest .
```

Multi-stage build:

| Stage | Base | Purpose |
|---|---|---|
| `builder` | `node:22-alpine` | Install deps via npm ci, compile TypeScript + Vite build |
| runtime | `nginx:alpine` | Copy `dist/` + `nginx.conf` |

The nginx configuration serves the SPA and reverse-proxies `/api/` and `/ws/` to the API container.

## Kubernetes (Kind)

```bash
# Create local cluster
make kind-create

# Deploy the Helm chart
make helm-install
# Access: kubectl port-forward -n aiops svc/aiops-assistant 8000:8000

# Clean up
make helm-uninstall
make kind-delete
```

The Helm chart creates:

| Resource | Name | Details |
|---|---|---|
| ConfigMap | `{release}-config` | API_HOST, API_PORT, QDRANT_HOST, LLM_MODEL, OTEL_ENDPOINT |
| Deployment | `{release}` | 1 replica (configurable), probes on /health, resource limits |
| Service | `{release}` | ClusterIP :8000 |
| Ingress | `{release}` | Disabled by default, host: `aiops.local` |

**Required secret** — create before deploying:

```bash
kubectl create secret generic aiops-assistant \
  --from-literal=OPENROUTER_API_KEY=sk-or-v1-...
```

## GitHub Container Registry (GHCR)

The CI pipeline (`ci.yml`) automatically builds and pushes the backend image to `ghcr.io/seydinabane/aiops-assistant` on every push to `main`. Tags:

- `main` — most recent main push
- `{sha}` — commit SHA
- `semver` — on release tags

The frontend is not pushed to GHCR — it's built from source in the docker-compose file.

## CI/CD pipeline

### `ci.yml` (push/PR to main)

```
quality:  ruff check → ruff format --check → mypy src
test:     pytest --cov --cov-fail-under=80 → pre-commit run --all-files
frontend: npm ci → npm run build (type check + Vite build)
build:    (main only) docker buildx → tag → push to GHCR
```

Quality, test, and frontend run in parallel. Build waits for all three and only runs on main.

### `docker.yml` (release publish or manual dispatch)

```
Checkout → Docker metadata → buildx → push (semver + latest)
```

## Environment variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `OPENROUTER_API_KEY` | — | Yes | OpenRouter API key |
| `API_HOST` | `0.0.0.0` | No | Bind address |
| `API_PORT` | `8000` | No | HTTP port |
| `API_LOG_LEVEL` | `INFO` | No | Log level (DEBUG for dev) |
| `LLM_MODEL` | `openai/gpt-4o-mini` | No | Model identifier |
| `LLM_MAX_TOKENS` | `4096` | No | Max response tokens |
| `LLM_TEMPERATURE` | `0.1` | No | LLM temperature |
| `QDRANT_HOST` | `localhost` | No | Qdrant hostname |
| `QDRANT_PORT` | `6333` | No | Qdrant gRPC port |
| `QDRANT_GRPC_PORT` | `6334` | No | Qdrant gRPC internal port |
| `COLLECTION_NAME` | `runbooks` | No | Qdrant collection name |
| `OTEL_SERVICE_NAME` | `aiops-assistant` | No | OpenTelemetry service name |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4318` | No | OTLP HTTP endpoint |
| `FRONTEND_PORT` | `80` | No | Frontend nginx port |

## Health check

The API exposes `/health` returning `{"status": "ok"}`. Docker and K8s both use this for liveness and readiness probes.

## Monitoring

The docker-compose stack includes:

- **OpenTelemetry Collector** — receives traces from the API via OTLP HTTP, exports to the configured backend
- **Prometheus** — scrapes the API's metrics endpoint every 15s (requires `opentelemetry-instrumentation-fastapi`)

Metrics and traces are opt-in: the API starts without OTEL if the collector is unreachable.

## Security

- Non-root container user (`appuser`)
- No secrets in the image (env vars at runtime)
- Security linting via `bandit` in pre-commit
- `safety` check in CI (not yet enabled — add with `uv add --dev safety`)
- Dependency pinning via `uv.lock` (reproducible builds)
