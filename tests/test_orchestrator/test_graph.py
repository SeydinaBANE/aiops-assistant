from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.domain.incident import Alert, Incident, InvestigationStep, Severity
from src.orchestrator.graph import build_graph, run_investigation


@pytest.fixture
def incident() -> Incident:
    return Incident(
        alert=Alert(
            title="Disk Space Alert",
            message="Disk usage exceeded 90%.",
            source="grafana",
            severity=Severity.HIGH,
            labels={"alertname": "disk-full", "host": "web-01"},
        ),
    )


@pytest.mark.asyncio
async def test_run_investigation_all_success(incident: Incident) -> None:
    logs = AsyncMock()
    logs.investigate = AsyncMock(return_value=InvestigationStep(agent_name="logs", status="success", result="logs ok"))
    knowledge = AsyncMock()
    knowledge.investigate = AsyncMock(
        return_value=InvestigationStep(agent_name="knowledge", status="success", result="knowledge ok"),
    )
    remediation = AsyncMock()
    remediation.investigate = AsyncMock(
        return_value=InvestigationStep(agent_name="remediation", status="success", result="fix it"),
    )

    result = await run_investigation(incident, logs, knowledge, remediation)
    assert result.status == "resolved"
    assert result.summary is not None


@pytest.mark.asyncio
async def test_run_investigation_agent_failure(incident: Incident) -> None:
    logs = AsyncMock()
    logs.investigate = AsyncMock(
        return_value=InvestigationStep(agent_name="logs", status="success", result="ok"),
    )
    knowledge = AsyncMock()
    knowledge.investigate = AsyncMock(side_effect=ValueError("Qdrant unavailable"))
    remediation = AsyncMock()
    remediation.investigate = AsyncMock(
        return_value=InvestigationStep(agent_name="remediation", status="success", result="fix"),
    )

    # Should not raise — error is caught in the node
    result = await run_investigation(incident, logs, knowledge, remediation)
    # One agent failed => incident fails
    error_agents = [s.agent_name for s in result.investigation_log if s.status == "error"]
    assert len(error_agents) > 0
    assert result.status in ("failed", "investigating")


def test_build_graph() -> None:
    logs = AsyncMock()
    knowledge = AsyncMock()
    remediation = AsyncMock()
    graph = build_graph(logs, knowledge, remediation)
    assert graph is not None
