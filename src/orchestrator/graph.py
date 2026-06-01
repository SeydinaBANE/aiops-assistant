from __future__ import annotations

import time
from typing import TYPE_CHECKING, cast

from langgraph.graph import StateGraph

from src.domain.incident import Incident, IncidentStatus, InvestigationStep
from src.orchestrator.state import IncidentState

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from langgraph.graph.state import CompiledStateGraph

    from src.agents.protocol import Agent


class AgentNode:
    def __init__(self, name: str, investigate_fn: Callable[[Incident], Awaitable[InvestigationStep]]) -> None:
        self.name = name
        self._investigate = investigate_fn

    async def __call__(self, state: IncidentState) -> dict[str, Incident]:
        incident = state["incident"]
        start = time.perf_counter()
        try:
            step = await self._investigate(incident)
            elapsed = (time.perf_counter() - start) * 1000
            step.duration_ms = elapsed
            incident.add_step(step)
            return {"incident": incident}
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            step = InvestigationStep(
                agent_name=self.name,
                status="error",
                error=str(exc),
                duration_ms=elapsed,
            )
            incident.add_step(step)
            return {"incident": incident}


def build_graph(
    logs_agent: Agent, knowledge_agent: Agent, remediation_agent: Agent
) -> CompiledStateGraph[IncidentState]:
    workflow = StateGraph(IncidentState)

    logs_node = AgentNode("logs", logs_agent.investigate)
    knowledge_node = AgentNode("knowledge", knowledge_agent.investigate)
    remediation_node = AgentNode("remediation", remediation_agent.investigate)

    workflow.add_node("logs", logs_node)
    workflow.add_node("knowledge", knowledge_node)
    workflow.add_node("remediation", remediation_node)

    workflow.set_entry_point("logs")
    workflow.add_edge("logs", "knowledge")
    workflow.add_edge("knowledge", "remediation")
    workflow.add_edge("remediation", "__end__")

    return workflow.compile()


async def run_investigation(
    incident: Incident,
    logs_agent: Agent,
    knowledge_agent: Agent,
    remediation_agent: Agent,
) -> Incident:
    graph = build_graph(logs_agent, knowledge_agent, remediation_agent)
    initial_state: IncidentState = {"incident": incident}
    incident.status = IncidentStatus.INVESTIGATING

    final_state = cast("IncidentState", await graph.ainvoke(initial_state))
    result = final_state["incident"]
    if all(s.status == "success" for s in result.investigation_log):
        result.resolve(
            "\n\n".join(f"## {s.agent_name}\n{s.result}" for s in result.investigation_log if s.status == "success")
        )
    else:
        errors = [s.error for s in result.investigation_log if s.error]
        result.fail("; ".join(errors))
    return result
