"""Incident route/service tests using test-only persistence."""

import pytest

from app.services.incidents import IncidentNotFoundError
from tests.unit.conftest import Harness


def test_create_retrieve_and_unique_ids(harness: Harness, incident_payload: dict[str, str]) -> None:
    first = harness.client.post("/incidents", json=incident_payload)
    second = harness.client.post("/incidents", json=incident_payload)
    assert first.status_code == second.status_code == 201
    assert set(first.json()) == {"incidentId", "status"}
    assert first.json()["status"] == "OPEN"
    assert first.json()["incidentId"] != second.json()["incidentId"]
    response = harness.client.get(f"/incidents/{first.json()['incidentId']}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == incident_payload["title"]
    assert data["description"] == incident_payload["description"]
    assert data["reporterName"] == incident_payload["reporterName"]
    assert data["discoveredAt"] == "2020-01-01T14:00:00Z"
    assert data["evidence"] == []
    assert data["currentDecision"] is data["filing"] is None
    assert "createdAt" not in data


@pytest.mark.parametrize("field", ["title", "description", "discoveredAt", "reporterName"])
def test_missing_fields_leave_no_records(
    harness: Harness, incident_payload: dict[str, str], field: str
) -> None:
    del incident_payload[field]
    response = harness.client.post("/incidents", json=incident_payload)
    assert response.status_code == 400
    assert set(response.json()) == {"error", "message"}
    assert harness.repository.incidents == {}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("description", ""),
        ("title", "  "),
        ("discoveredAt", "2020-01-01T00:00:00"),
        ("discoveredAt", "9999-01-01T00:00:00Z"),
        ("discoveredAt", "bad"),
    ],
)
def test_invalid_input_no_write(
    harness: Harness, incident_payload: dict[str, str], field: str, value: str
) -> None:
    incident_payload[field] = value
    assert harness.client.post("/incidents", json=incident_payload).status_code == 400
    assert harness.repository.incidents == {}


def test_unknown_incident(harness: Harness) -> None:
    response = harness.client.get("/incidents/unknown")
    assert response.status_code == 404
    assert response.json() == {"error": "NOT_FOUND", "message": "Incident not found"}
    with pytest.raises(IncidentNotFoundError):
        harness.service.get_incident("unknown")


def test_malformed_json_and_append_only(harness: Harness) -> None:
    response = harness.client.post(
        "/incidents", content="{", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert harness.repository.incidents == {}
    assert harness.client.delete("/incidents/unknown").status_code == 405
    assert harness.client.put("/incidents/unknown", json={}).status_code == 405


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("description", ""),
        ("discoveredAt", "2020-01-01T00:00:00"),
        ("discoveredAt", "9999-01-01T00:00:00Z"),
    ],
)
def test_validation_errors_name_field(
    harness: Harness, incident_payload: dict[str, str], field: str, value: str
) -> None:
    response = harness.client.post("/incidents", json={**incident_payload, field: value})
    assert response.status_code == 400
    assert field in response.json()["message"]
    assert harness.repository.incidents == {}
