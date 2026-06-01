from typing import TypedDict

from src.domain.incident import Incident


class IncidentState(TypedDict):
    incident: Incident
