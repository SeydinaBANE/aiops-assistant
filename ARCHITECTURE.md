# Architecture

## Overview

AIOps Assistant is an event-driven system that ingests monitoring alerts, runs a multi-agent investigation pipeline orchestrated by LangGraph, and produces an incident report with root cause analysis and remediation steps.

```
┌─────────────┐     ┌──────────┐     ┌──────────────────────────────────────┐
│   Grafana   │────▶│  FastAPI  │────▶│         LangGraph Pipeline           │
│  Webhook    │     │ :8000    │     │  ┌──────┐  ┌──────────┐  ┌─────────┐ │
└─────────────┘     └──────────┘     │  │ Logs │─▶│Knowledge │─▶│Remediat.│ │
                                      │  │Agent │  │  Agent   │  │  Agent  │ │
                                      │  └──────┘  └──────────┘  └─────────┘ │
                                      └──────────┬───────────────────────────┘
                                                  │
                     ┌────────────────────────────┼────────────────────────────┐
                     │                            │                            │
                     ▼                            ▼                            ▼
              ┌─────────────┐            ┌─────────────────┐          ┌──────────────┐
              │  OpenRouter │            │  Qdrant (RAG)   │          │  OpenTelemetry│
              │  LLM API   │            │  + embeddings   │          │  + Prometheus │
              └─────────────┘            └─────────────────┘          └──────────────┘
```

## Components

### 1. API Layer (`src/api/`)

FastAPI application with three endpoints:

- `POST /incidents` — ingests an alert, spawns an async investigation, returns the incident
- `GET /incidents` — lists all incidents sorted by creation date (newest first)
- `GET /incidents/{id}` — returns a single incident with its full investigation log
- `GET /health` — liveness probe for Docker/K8s

Incidents are stored in-memory in a `dict[str, Incident]`. The API is stateless beyond this store; restarting clears all data. A production deployment would replace this with a database.

### 2. Agent System (`src/agents/`)

Three agents implement the `Agent` protocol defined in `protocol.py`:

```python
class Agent(Protocol):
    name: str
    async def investigate(incident: Incident) -> InvestigationStep: ...
```

**LogsAgent** — simulates fetching logs from a monitoring system. It matches the alert name against a mock database, then calls the LLM to analyze the logs and identify relevant patterns.

**KnowledgeAgent** — performs RAG over IT runbooks stored in Qdrant. It embeds the incident message with `sentence-transformers/all-MiniLM-L6-v2`, searches the vector store for similar runbooks, then asks the LLM to extract actionable knowledge from the results.

**RemediationAgent** — generates a step-by-step remediation plan using the LLM, conditioned on the incident severity (critical/high alerts get more urgent tone and explicit escalation steps).

### 3. Orchestrator (`src/orchestrator/`)

Uses LangGraph's `StateGraph` to define a sequential pipeline:

```
Logs Agent ──▶ Knowledge Agent ──▶ Remediation Agent ──▶ [end]
```

Each step is wrapped in an `AgentNode` that:
1. Times the execution
2. Catches exceptions and records them as error steps (the pipeline continues even if one agent fails)
3. Adds the `InvestigationStep` to the incident's investigation log

After the pipeline completes:
- If all steps succeeded → incident is marked `RESOLVED` with a merged summary
- If any step failed → incident is marked `FAILED` with concatenated error messages

The state is a simple `TypedDict` with a single key `incident: Incident`.

### 4. Domain Models (`src/domain/`)

```
Alert ──────────────▶ Incident ──────────────▶ list[InvestigationStep]
- id (uuid hex[:12])  - id                      - agent_name
- title               - alert                   - status (running/success/error)
- message             - status                  - result
- severity            - summary                 - error
- labels              - error                   - duration_ms
- source              - investigation_log       - timestamp
```

### 5. LLM Service (`src/services/llm.py`)

Lazy-initialized singleton client to OpenRouter's API:

```python
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=settings.openrouter_api_key)
```

The model and temperature are configurable via environment variables. Default model is `openai/gpt-4o-mini` with `temperature=0.1` (low — we want deterministic investigation results).

### 6. Vector Store (`src/infrastructure/vector_store.py`)

Qdrant client with lazy initialization — the connection is established on first access, not at import time. This allows tests and scripts to import the module without running Qdrant.

```
Embeddings: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
Distance: COSINE
Collection: "runbooks" (auto-created)
```

The `ingest()` method encodes documents and upserts them as points. The `search()` method returns the top-k payloads (title + content + tags).

### 7. Observability (`src/infrastructure/`)

**Logging** — structlog with two renderers:
- JSON in production (structured, machine-parseable)
- Console with colors in DEBUG mode (human-friendly)

**Tracing** — OpenTelemetry with OTLP HTTP exporter to an OpenTelemetry Collector, which forwards to Prometheus or any OTLP-compatible backend.

## Data Flow

```
1. User/script POSTs an alert to /incidents
2. API creates an Incident (status=PENDING)
3. API changes status to INVESTIGATING
4. run_investigation() builds the LangGraph and invokes it:
   a. LogsAgent investigates (mock logs + LLM analysis)
   b. KnowledgeAgent searches Qdrant runbooks + LLM synthesis
   c. RemediationAgent generates step-by-step plan via LLM
5. Pipeline completes → status = RESOLVED or FAILED
6. Incident is stored in _incidents dict
7. API returns the full IncidentResponse
```

## Design Decisions

| Decision | Rationale |
|---|---|
| **LangGraph over DAG** | State machine model fits the sequential agent pipeline better than a DAG runner. Each step has access to the accumulated state. |
| **OpenRouter over direct API** | Model-agnostic. Swap `openai/gpt-4o-mini` for `anthropic/claude-sonnet` or `google/gemini-pro` via env var — no code change. |
| **Qdrant over FAISS/Pinecone** | Qdrant runs locally in Docker (no cloud dependency), has gRPC for low-latency, and supports filtering. |
| **`sentence-transformers` over OpenAI embeddings** | No API call needed for embedding — runs locally, faster for small-scale RAG, zero cost. |
| **In-memory incident store** | Simplifies the MVP. Replace with PostgreSQL/Redis in production. |
| **Sequential agents over parallel** | Investigation is inherently sequential: you need logs before knowledge, knowledge before remediation. Parallel execution would not change the outcome. |
| **Lazy VectorStore init** | Tests and CLI scripts can import the module without Qdrant running. Client connects on first property access. |
| **Low LLM temperature (0.1)** | Investigation output should be deterministic and factual, not creative. |
| **structlog over logging** | Structured output is essential for production observability. JSON logs integrate with Loki/ELK. JSON in production, pretty-print in dev. |
| **Multi-stage Docker** | Builder stage compiles deps; runtime stage is minimal `python:3.12-slim` with non-root user — smaller image, smaller attack surface. |
| **OpenTelemetry + Prometheus** | Vendor-neutral observability. Collector buffers and retries; Prometheus provides long-term metrics storage. |

## Project Structure

```
src/
├── api/               # REST endpoints (routes.py, schemas.py)
│   routes.py          # FastAPI router: POST/GET /incidents, /health
│   schemas.py         # Pydantic request/response models
├── agents/            # Multi-agent system
│   protocol.py        # Agent protocol (interface)
│   logs_agent.py      # LogsAgent + KnowledgeAgent + RemediationAgent
├── orchestrator/      # LangGraph state machine
│   graph.py           # build_graph(), run_investigation(), AgentNode
│   state.py           # IncidentState TypedDict
├── domain/            # Core domain models
│   incident.py        # Alert, Incident, InvestigationStep, enums
├── infrastructure/    # Vector store, telemetry, logging
│   vector_store.py    # Qdrant + sentence-transformers wrapper
│   telemetry.py       # OpenTelemetry setup
│   logger.py          # structlog configuration
├── services/          # External service clients
│   llm.py             # OpenRouter client (get_client, ask_llm)
├── config.py          # Pydantic Settings (env-based)
└── main.py            # FastAPI app with lifespan
tests/
├── conftest.py        # Fixtures: client, mock_llm, sample_incident, mock_vector_store
├── test_api/          # API endpoint tests
├── test_agents/       # Agent unit tests (all 3 agents)
└── test_orchestrator/ # LangGraph pipeline tests
scripts/
├── seed_knowledge.py  # Seed Qdrant with runbooks
└── simulate_alert.py  # POST mock alerts to the API
data/runbooks/         # IT runbooks (disk-full, high-cpu, service-down)
```
