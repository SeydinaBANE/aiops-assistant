# Demo Script (5 min)

## Prerequisites
- Docker running
- `OPENROUTER_API_KEY` set in `.env`

## Step 1 — Start (30s)

```bash
make docker-up
```

Wait for healthy: `docker compose ps`

## Step 2 — Seed knowledge (30s)

```bash
uv run scripts/seed_knowledge.py
```

Expected: "Ingested 3 runbooks into Qdrant collection 'runbooks'."

## Step 3 — Trigger incident (30s)

```bash
uv run scripts/simulate_alert.py disk-full
```

## Step 4 — Inspect results (1 min)

```bash
# List all incidents
curl http://localhost:8000/incidents | python -m json.tool

# Get latest incident ID
INCIDENT_ID=$(curl -s http://localhost:8000/incidents | python -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# Show full investigation
curl http://localhost:8000/incidents/$INCIDENT_ID | python -m json.tool
```

## Step 5 — Multiple alerts (1 min)

```bash
uv run scripts/simulate_alert.py high-cpu
uv run scripts/simulate_alert.py service-down
curl http://localhost:8000/incidents | python -c "
import sys, json
incidents = json.load(sys.stdin)
for i in incidents:
    print(f'{i[\"id\"][:8]} | {i[\"alert_title\"]:25s} | {i[\"status\"]:12s} | {len(i[\"steps\"])} steps')
"
```

## Key talking points
- Each investigation runs 3 agents in sequence via LangGraph
- Knowledge agent uses RAG (semantic search on runbooks)
- LLM calls go through OpenRouter (model-agnostic)
- Full OpenTelemetry traces between agents
- CI/CD: lint → typecheck → test → build → push to GHCR
