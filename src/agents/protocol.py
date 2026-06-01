from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.domain.incident import Incident, InvestigationStep


class Agent(Protocol):
    name: str

    async def investigate(self, incident: Incident) -> InvestigationStep: ...
