from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.logs_agent import KnowledgeAgent
from src.domain.incident import Alert, Incident, Severity


@pytest.fixture
def mock_store() -> MagicMock:
    store = MagicMock()
    store.search.return_value = [
        {
            "title": "Disk Full Runbook",
            "content": "Steps to clear disk space.",
            "tags": ["disk-full"],
        },
    ]
    return store


@pytest.fixture
def agent(mock_store: MagicMock) -> KnowledgeAgent:
    return KnowledgeAgent(mock_store)


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
async def test_investigate_with_results(agent: KnowledgeAgent, incident: Incident, mock_llm: AsyncMock) -> None:
    step = await agent.investigate(incident)
    assert step.agent_name == "knowledge"
    assert step.status == "success"
    assert len(step.result) > 0


@pytest.mark.asyncio
async def test_investigate_no_results(mock_store: MagicMock) -> None:
    mock_store.search.return_value = []
    agent = KnowledgeAgent(mock_store)
    incident = Incident(
        alert=Alert(
            title="Unknown Alert",
            message="Something weird.",
            source="grafana",
            severity=Severity.LOW,
            labels={"alertname": "unknown"},
        ),
    )
    step = await agent.investigate(incident)
    assert step.status == "success"
    assert "No relevant runbooks" in step.result
