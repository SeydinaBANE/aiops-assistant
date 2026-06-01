from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.agents.logs_agent import RemediationAgent
from src.domain.incident import Alert, Incident, Severity


@pytest.fixture
def agent() -> RemediationAgent:
    return RemediationAgent()


@pytest.fixture
def incident() -> Incident:
    return Incident(
        alert=Alert(
            title="Disk Space Alert",
            message="Disk usage exceeded 90% threshold.",
            source="grafana",
            severity=Severity.CRITICAL,
            labels={"alertname": "disk-full", "host": "web-01"},
        ),
    )


@pytest.mark.asyncio
async def test_investigate_returns_plan(agent: RemediationAgent, incident: Incident, mock_llm: AsyncMock) -> None:
    step = await agent.investigate(incident)
    assert step.agent_name == "remediation"
    assert step.status == "success"
    assert len(step.result) > 0


@pytest.mark.asyncio
async def test_investigate_low_severity(agent: RemediationAgent, mock_llm: AsyncMock) -> None:
    incident = Incident(
        alert=Alert(
            title="Minor Issue",
            message="Disk usage at 75%.",
            source="grafana",
            severity=Severity.LOW,
            labels={"alertname": "disk-full"},
        ),
    )
    step = await agent.investigate(incident)
    assert step.status == "success"
