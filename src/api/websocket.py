from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.agents.logs_agent import KnowledgeAgent, LogsAgent, RemediationAgent
from src.api.routes import _incidents, _to_response
from src.api.schemas import AlertRequest
from src.domain.incident import Alert, Incident, InvestigationStep
from src.infrastructure.logger import get_logger
from src.infrastructure.vector_store import VectorStore
from src.orchestrator.graph import run_investigation

ws_router = APIRouter()
logger = get_logger(__name__)

_vector_store = VectorStore()
_logs_agent = LogsAgent()
_knowledge_agent = KnowledgeAgent(_vector_store)
_remediation_agent = RemediationAgent()


@ws_router.websocket("/ws/incidents")
async def incident_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        alert_req = AlertRequest(**data)
        alert = Alert(
            title=alert_req.title,
            message=alert_req.message,
            source=alert_req.source,
            severity=alert_req.severity,
            labels=alert_req.labels,
        )
        incident = Incident(alert=alert)
        _incidents[incident.id] = incident

        await websocket.send_json({"type": "investigating", "incident_id": incident.id})

        async def on_step(step: InvestigationStep) -> None:
            await websocket.send_json(
                {
                    "type": "step",
                    "step": step.model_dump(mode="json"),
                }
            )

        result = await run_investigation(
            incident,
            logs_agent=_logs_agent,
            knowledge_agent=_knowledge_agent,
            remediation_agent=_remediation_agent,
            step_callback=on_step,
        )
        _incidents[result.id] = result

        response = _to_response(result)
        await websocket.send_json({"type": "complete", "incident": response.model_dump(mode="json")})

    except WebSocketDisconnect:
        logger.info("Client disconnected during investigation")
    except Exception:
        logger.exception("WebSocket investigation failed")
        await websocket.send_json({"type": "error", "message": "Investigation failed"})
