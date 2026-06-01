from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.domain.incident import Alert, Incident
from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_llm() -> AsyncMock:
    with patch("src.agents.logs_agent.ask_llm", return_value="Mocked LLM response.") as m:
        yield m


@pytest.fixture
def sample_incident() -> Incident:
    return Incident(
        alert=Alert(
            title="Disk Space Alert",
            message="Disk usage exceeded 90%.",
            source="grafana",
            severity="high",
            labels={"alertname": "disk-full", "host": "web-01"},
        ),
    )


@pytest.fixture
def mock_vector_store() -> AsyncIterator[MagicMock]:
    store = MagicMock()
    store.search.return_value = [
        {
            "title": "Disk Full Runbook",
            "content": "Clean logs: find /var/log -name *.log -delete",
            "tags": ["disk-full"],
        },
    ]
    with patch("src.api.routes._vector_store", store):
        yield store
