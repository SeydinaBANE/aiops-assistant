from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.domain.incident import Alert, Incident


@patch("src.api.websocket.run_investigation")
class TestWebSocketIncident:
    def test_ws_investigation_streams_steps(self, mock_investigation, client: TestClient) -> None:
        result = Incident(
            alert=Alert(title="Test", message="Test", source="grafana", severity="high"),
        )
        result.status = "resolved"
        result.summary = "All checks passed"
        mock_investigation.return_value = result

        payload = {
            "title": "Disk Space Alert",
            "message": "Disk usage exceeded 90%.",
            "severity": "high",
        }

        with client.websocket_connect("/ws/incidents") as ws:
            ws.send_json(payload)

            investigating = ws.receive_json()
            assert investigating["type"] == "investigating"
            assert "incident_id" in investigating

            complete = ws.receive_json()
            assert complete["type"] == "complete"
            assert complete["incident"]["alert_title"] == "Test"
            assert complete["incident"]["summary"] == "All checks passed"

    def test_ws_invalid_json_returns_error(self, mock_investigation, client: TestClient) -> None:
        with client.websocket_connect("/ws/incidents") as ws:
            ws.send_text("not-json")
            response = ws.receive_json()
            assert response["type"] == "error"
