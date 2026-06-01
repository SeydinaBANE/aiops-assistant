from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(StrEnum):
    PENDING = "pending"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FAILED = "failed"


class Alert(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    title: str
    message: str
    source: str = "grafana"
    severity: Severity
    labels: dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Incident(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    alert: Alert
    status: IncidentStatus = IncidentStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    investigation_log: list[InvestigationStep] = Field(default_factory=list)
    summary: str | None = None
    error: str | None = None

    def add_step(self, step: InvestigationStep) -> None:
        self.investigation_log.append(step)
        self.updated_at = datetime.now(UTC)

    def resolve(self, summary: str) -> None:
        self.status = IncidentStatus.RESOLVED
        self.summary = summary
        self.updated_at = datetime.now(UTC)

    def fail(self, error: str) -> None:
        self.status = IncidentStatus.FAILED
        self.summary = error
        self.error = error
        self.updated_at = datetime.now(UTC)


class InvestigationStep(BaseModel):
    agent_name: str
    status: Literal["running", "success", "error"]
    result: str = ""
    error: str | None = None
    duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
