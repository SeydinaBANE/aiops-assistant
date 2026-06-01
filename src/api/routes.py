from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.agents.logs_agent import KnowledgeAgent, LogsAgent, RemediationAgent
from src.api.schemas import AlertRequest, IncidentResponse, InvestigationStepResponse
from src.domain.incident import Alert, Incident
from src.infrastructure.vector_store import VectorStore
from src.orchestrator.graph import run_investigation

router = APIRouter()

_incidents: dict[str, Incident] = {}

_vector_store = VectorStore()
_logs_agent = LogsAgent()
_knowledge_agent = KnowledgeAgent(_vector_store)
_remediation_agent = RemediationAgent()


def _to_response(incident: Incident) -> IncidentResponse:
    return IncidentResponse(
        id=incident.id,
        alert_title=incident.alert.title,
        alert_severity=incident.alert.severity,
        status=incident.status,
        steps=[
            InvestigationStepResponse(
                agent_name=s.agent_name,
                status=s.status,
                result=s.result,
                error=s.error,
                duration_ms=s.duration_ms,
                timestamp=s.timestamp,
            )
            for s in incident.investigation_log
        ],
        summary=incident.summary,
        error=incident.error,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )


@router.post("/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(payload: AlertRequest) -> IncidentResponse:
    alert = Alert(
        title=payload.title,
        message=payload.message,
        source=payload.source,
        severity=payload.severity,
        labels=payload.labels,
    )
    incident = Incident(alert=alert)
    _incidents[incident.id] = incident

    result = await run_investigation(
        incident,
        logs_agent=_logs_agent,
        knowledge_agent=_knowledge_agent,
        remediation_agent=_remediation_agent,
    )

    _incidents[result.id] = result
    return _to_response(result)


@router.get("/incidents", response_model=list[IncidentResponse])
async def list_incidents() -> list[IncidentResponse]:
    return [_to_response(i) for i in sorted(_incidents.values(), key=lambda x: x.created_at, reverse=True)]


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str) -> IncidentResponse:
    incident = _incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _to_response(incident)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
