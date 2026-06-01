from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from src.domain.incident import Incident, InvestigationStep
from src.services.llm import ask_llm

if TYPE_CHECKING:
    from src.infrastructure.vector_store import VectorStore

_LOG_DATABASE: dict[str, list[dict[str, str]]] = {
    "disk-full": [
        {"timestamp": "2026-06-01T10:00:00Z", "level": "ERROR", "message": "disk usage at 98% on /dev/sda1"},
        {"timestamp": "2026-06-01T10:01:00Z", "level": "WARN", "message": "inode usage at 85%"},
        {"timestamp": "2026-06-01T10:02:00Z", "level": "ERROR", "message": "write operation timed out on /var/log"},
    ],
    "high-cpu": [
        {"timestamp": "2026-06-01T09:30:00Z", "level": "WARN", "message": "CPU at 92% sustained for 5m"},
        {"timestamp": "2026-06-01T09:31:00Z", "level": "WARN", "message": "top consumer: python3 PID 1024 at 340%"},
        {"timestamp": "2026-06-01T09:32:00Z", "level": "ERROR", "message": "load average 12.5 — threshold exceeded"},
    ],
    "service-down": [
        {"timestamp": "2026-06-01T08:00:00Z", "level": "CRITICAL", "message": "port 443 unreachable"},
        {"timestamp": "2026-06-01T08:01:00Z", "level": "CRITICAL", "message": "healthcheck: api-gateway unreachable"},
        {"timestamp": "2026-06-01T08:02:00Z", "level": "ERROR", "message": "connection pool exhausted for backend-svc"},
    ],
}


class LogsAgent:
    name = "logs"

    async def investigate(self, incident: Incident) -> InvestigationStep:
        await asyncio.sleep(0.1)
        alert = incident.alert
        key = alert.labels.get("alertname", "unknown")
        logs = _LOG_DATABASE.get(key, [])

        if not logs:
            return InvestigationStep(
                agent_name=self.name,
                status="success",
                result="No relevant logs found for this alert.",
            )

        log_text = "\n".join(f"[{e['timestamp']}] {e['level']}: {e['message']}" for e in logs)

        analysis = ask_llm(
            system_prompt="You are a senior SRE analyzing logs. Be concise.",
            user_prompt=f"Alert: {alert.title}\n{alert.message}\n\nLogs:\n{log_text}\n\nSummarize the root cause:",
        )

        return InvestigationStep(
            agent_name=self.name,
            status="success",
            result=analysis,
        )


class KnowledgeAgent:
    name = "knowledge"

    def __init__(self, vector_store: VectorStore) -> None:
        self._vector_store = vector_store

    async def investigate(self, incident: Incident) -> InvestigationStep:
        await asyncio.sleep(0.1)
        docs = self._vector_store.search(incident.alert.title, top_k=2)

        if not docs:
            return InvestigationStep(
                agent_name=self.name,
                status="success",
                result="No relevant runbooks found in knowledge base.",
            )

        context = "\n\n".join(f"# {d['title']}\n{d['content']}" for d in docs)

        user = f"Alert: {incident.alert.title}\n\nRelevant runbooks:\n{context}\n\nWhat remediation steps apply?"
        summary = ask_llm(
            system_prompt="You are an IT Ops knowledge expert. Extract actionable steps from runbooks.",
            user_prompt=user,
        )

        return InvestigationStep(
            agent_name=self.name,
            status="success",
            result=summary,
        )


class RemediationAgent:
    name = "remediation"

    async def investigate(self, incident: Incident) -> InvestigationStep:
        await asyncio.sleep(0.1)

        plan = ask_llm(
            system_prompt="You are an automation engineer. Generate a concrete remediation plan.",
            user_prompt=(
                f"Alert: {incident.alert.title}\n{incident.alert.message}\n"
                f"Severity: {incident.alert.severity}\n\n"
                "Propose a step-by-step remediation plan with specific commands:"
            ),
        )

        return InvestigationStep(
            agent_name=self.name,
            status="success",
            result=plan,
        )
