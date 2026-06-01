from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCreateIncident:
    @patch("src.api.routes.run_investigation")
    def test_create_incident_success(self, mock_investigation, client: TestClient) -> None:
        from src.domain.incident import Alert, Incident, Severity

        mock_investigation.return_value = Incident(
            alert=Alert(title="Test", message="Test", source="grafana", severity=Severity.HIGH),
        )
        mock_investigation.return_value.investigation_log = []
        mock_investigation.return_value.status = "resolved"
        mock_investigation.return_value.summary = "All good"

        payload = {
            "title": "Disk Space Alert",
            "message": "Disk usage exceeded 90%.",
            "source": "grafana",
            "severity": "high",
            "labels": {"alertname": "disk-full"},
        }
        response = client.post("/incidents", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "resolved"
        assert data["alert_title"] == "Test"

    @patch("src.api.routes.run_investigation")
    def test_create_incident_with_minimal_payload(self, mock_investigation, client: TestClient) -> None:
        from src.domain.incident import Alert, Incident, Severity

        mock_investigation.return_value = Incident(
            alert=Alert(title="CPU Alert", message="CPU high", source="grafana", severity=Severity.MEDIUM),
        )
        mock_investigation.return_value.investigation_log = []
        mock_investigation.return_value.status = "resolved"
        mock_investigation.return_value.summary = "done"

        payload = {"title": "CPU Alert", "message": "CPU high"}
        response = client.post("/incidents", json=payload)
        assert response.status_code == 201


class TestListIncidents:
    @patch("src.api.routes.run_investigation")
    @patch("src.api.routes._incidents", {})
    def test_list_empty(self, mock_investigation, client: TestClient) -> None:
        response = client.get("/incidents")
        assert response.status_code == 200
        assert response.json() == []

    @patch("src.api.routes.run_investigation")
    @patch("src.api.routes._incidents", {})
    def test_list_after_creation(self, mock_investigation, client: TestClient) -> None:
        from src.domain.incident import Alert, Incident, Severity

        mock_investigation.return_value = Incident(
            alert=Alert(title="Test", message="Test", source="grafana", severity=Severity.MEDIUM),
        )
        mock_investigation.return_value.investigation_log = []
        mock_investigation.return_value.status = "resolved"
        mock_investigation.return_value.summary = "done"

        client.post("/incidents", json={"title": "T1", "message": "M1"})
        response = client.get("/incidents")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    @patch("src.api.routes.run_investigation")
    @patch("src.api.routes._incidents", {})
    def test_get_nonexistent_incident(self, mock_investigation, client: TestClient) -> None:
        response = client.get("/incidents/nonexistent")
        assert response.status_code == 404
