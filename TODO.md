# TODO

## MVP (done)
- [x] Project structure with all config files
- [x] Domain models (Incident, Alert, AgentResult)
- [x] Multi-agent system (logs, knowledge, remediation)
- [x] LangGraph orchestration
- [x] FastAPI REST API with 4 endpoints
- [x] OpenRouter LLM integration
- [x] Qdrant vector store for RAG
- [x] Mock runbooks for knowledge base
- [x] OpenTelemetry traces
- [x] Structlog structured logging
- [x] Docker multi-stage build (distroless)
- [x] Docker Compose (api + qdrant + otel + prometheus)
- [x] GitHub Actions CI (lint → typecheck → test → build → push GHCR)
- [x] Helm chart for K8s deployment
- [x] Pre-commit hooks (ruff, mypy, bandit, security)
- [x] Makefile with all common commands
- [x] pytest suite with coverage ≥ 80%
- [x] uv package manager

## Next
- [ ] Real Splunk/Datadog integration (replace mock logs)
- [ ] ServiceNow ticket creation from incidents
- [ ] WebSocket for real-time investigation streaming
- [ ] Frontend dashboard (React)
- [ ] Incident deduplication
- [ ] Feedback loop (user rates investigation quality)
- [ ] Multi-tenant support
- [ ] SLO/SLI metrics collection

## Known issues
- Tests calling LLM are slow (mocked in unit tests, needs VCR for integration)
- No persistent storage for incidents (in-memory dict)
- Qdrant requires manual seeding via script
