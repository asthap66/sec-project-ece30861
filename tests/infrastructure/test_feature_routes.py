"""Real app/router/auth integration with a test-only repository (no PostgreSQL)."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.feature_support import get_incident_service
from app.services.incidents import IncidentService
from tests.infrastructure.conftest import TEST_KEY
from tests.unit.conftest import FakeRepository

KEY = {"X-API-Key": TEST_KEY}
INCIDENT = {
    "title": "Synthetic incident",
    "description": "Synthetic report",
    "discoveredAt": "2020-01-01T10:00:00-04:00",
    "reporterName": "Test team",
}
EVIDENCE = {
    "category": "BUSINESS_IMPACT",
    "summary": " Synthetic impact ",
    "source": "Synthetic logs",
    "collectedAt": "2020-01-01T11:00:00-04:00",
}


@pytest.fixture
def feature_client(app: FastAPI) -> Iterator[TestClient]:
    service = IncidentService(FakeRepository())
    app.dependency_overrides[get_incident_service] = lambda: service
    with TestClient(app) as client:
        yield client


def test_registered_workflow(feature_client: TestClient) -> None:
    created = feature_client.post("/incidents", json=INCIDENT, headers=KEY)
    assert created.status_code == 201
    assert set(created.json()) == {"incidentId", "status"}
    incident_id = created.json()["incidentId"]
    evidence = feature_client.post(f"/incidents/{incident_id}/evidence", json=EVIDENCE, headers=KEY)
    assert evidence.status_code == 201
    assert set(evidence.json()) == {"evidenceId", "recordedAt"}
    detail = feature_client.get(f"/incidents/{incident_id}", headers=KEY)
    assert detail.status_code == 200
    assert detail.json()["evidence"][0]["summary"] == EVIDENCE["summary"]
    assert detail.json()["status"] == "OPEN"
    assert detail.json()["discoveredAt"] == "2020-01-01T14:00:00Z"


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/incidents"),
        ("GET", "/incidents/INC-001"),
        ("POST", "/incidents/INC-001/evidence"),
    ],
)
@pytest.mark.parametrize("key", [None, "incorrect"])
def test_features_require_shared_auth(
    feature_client: TestClient, method: str, path: str, key: str | None
) -> None:
    headers = {} if key is None else {"X-API-Key": key}
    response = feature_client.request(method, path, headers=headers, content="{")
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_shared_errors_and_precedence(feature_client: TestClient) -> None:
    missing = feature_client.post("/incidents", json={"title": "Synthetic"}, headers=KEY)
    assert missing.status_code == 400
    assert missing.json()["error"] == "INVALID_DESCRIPTION"
    unknown = feature_client.post("/incidents/INC-404/evidence", content="{", headers=KEY)
    assert unknown.status_code == 404
    assert unknown.json()["error"] == "NOT_FOUND"
    for method in ("PUT", "PATCH", "DELETE"):
        response = feature_client.request(method, "/incidents/INC-001", headers=KEY)
        assert response.status_code == 405
        assert response.json()["error"] == "METHOD_NOT_ALLOWED"
