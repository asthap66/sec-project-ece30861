"""Test-only storage adapter; production must use Person 1's database."""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.evidence import router as evidence_router
from app.routes.feature_support import get_incident_service
from app.routes.incidents import router as incident_router
from app.schemas import EvidenceResponse, IncidentDetail
from app.services.incidents import IncidentNotFoundError, IncidentService


class FakeRepository:
    def __init__(self) -> None:
        self.incidents: dict[str, IncidentDetail] = {}

    def create_incident(self, incident: IncidentDetail) -> None:
        if incident.incident_id in self.incidents:
            raise ValueError("Duplicate incident ID")
        self.incidents[incident.incident_id] = incident.model_copy(deep=True)

    def get_incident(self, incident_id: str) -> IncidentDetail | None:
        incident = self.incidents.get(incident_id)
        return incident.model_copy(deep=True) if incident else None

    def add_evidence(self, incident_id: str, evidence: EvidenceResponse) -> None:
        if incident_id not in self.incidents:
            raise IncidentNotFoundError(incident_id)
        self.incidents[incident_id].evidence.append(evidence.model_copy(deep=True))


@dataclass
class Harness:
    client: TestClient
    repository: FakeRepository
    service: IncidentService


@pytest.fixture
def harness() -> Iterator[Harness]:
    repository = FakeRepository()
    service = IncidentService(repository, clock=lambda: datetime(2020, 1, 2, tzinfo=UTC))
    app = FastAPI()
    app.include_router(incident_router)
    app.include_router(evidence_router)
    app.dependency_overrides[get_incident_service] = lambda: service
    with TestClient(app) as client:
        yield Harness(client, repository, service)


@pytest.fixture
def incident_payload() -> dict[str, str]:
    return {
        "title": "Synthetic incident",
        "description": "Synthetic description",
        "discoveredAt": "2020-01-01T10:00:00-04:00",
        "reporterName": "Test team",
    }


@pytest.fixture
def evidence_payload() -> dict[str, str]:
    return {
        "category": "TECHNICAL",
        "summary": " Synthetic finding ",
        "source": "Synthetic logs",
        "collectedAt": "2020-01-01T11:00:00-04:00",
    }
