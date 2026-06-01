from datetime import datetime

from pydantic import BaseModel

from src.domain.incident import IncidentStatus, Severity


class AlertRequest(BaseModel):
    title: str
    message: str
    source: str = "grafana"
    severity: Severity = Severity.HIGH
    labels: dict[str, str] = {}


class InvestigationStepResponse(BaseModel):
    agent_name: str
    status: str
    result: str
    error: str | None = None
    duration_ms: float
    timestamp: datetime


class IncidentResponse(BaseModel):
    id: str
    alert_title: str
    alert_severity: Severity
    status: IncidentStatus
    steps: list[InvestigationStepResponse]
    summary: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
