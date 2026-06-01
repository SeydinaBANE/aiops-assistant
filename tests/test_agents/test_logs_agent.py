from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.agents.logs_agent import LogsAgent
from src.domain.incident import Alert, Incident, Severity


@pytest.fixture
def agent() -> LogsAgent:
    return LogsAgent()


@pytest.fixture
def disk_incident() -> Incident:
    return Incident(
        alert=Alert(
            title="Disk Space Alert",
            message="Disk usage exceeded 90%.",
            source="grafana",
            severity=Severity.HIGH,
            labels={"alertname": "disk-full", "host": "web-01"},
        ),
    )


@pytest.fixture
def unknown_incident() -> Incident:
    return Incident(
        alert=Alert(
            title="Unknown Alert",
            message="Something weird happened.",
            source="grafana",
            severity=Severity.LOW,
            labels={"alertname": "unknown-monster"},
        ),
    )


@pytest.mark.asyncio
async def test_investigate_known_alert(agent: LogsAgent, disk_incident: Incident, mock_llm: AsyncMock) -> None:
    step = await agent.investigate(disk_incident)
    assert step.agent_name == "logs"
    assert step.status == "success"
    assert len(step.result) > 0


@pytest.mark.asyncio
async def test_investigate_unknown_alert(agent: LogsAgent, unknown_incident: Incident) -> None:
    step = await agent.investigate(unknown_incident)
    assert step.status == "success"
    assert "No relevant logs found" in step.result
