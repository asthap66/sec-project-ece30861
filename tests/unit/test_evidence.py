"""Evidence routes and their relationship to incidents."""

import pytest

from tests.unit.conftest import Harness


def test_attach_and_retrieve(
    harness: Harness, incident_payload: dict[str, str], evidence_payload: dict[str, str]
) -> None:
    incident_id = harness.client.post("/incidents", json=incident_payload).json()["incidentId"]
    other_id = harness.client.post("/incidents", json=incident_payload).json()["incidentId"]
    identifiers = set()
    for category in ["TECHNICAL", "TECHNICAL", "TECHNICAL", "BUSINESS_IMPACT"]:
        evidence_payload["category"] = category
        response = harness.client.post(f"/incidents/{incident_id}/evidence", json=evidence_payload)
        assert response.status_code == 201
        assert set(response.json()) == {"evidenceId", "recordedAt"}
        assert response.json()["recordedAt"] == "2020-01-02T00:00:00Z"
        identifiers.add(response.json()["evidenceId"])
    assert len(identifiers) == 4
    data = harness.client.get(f"/incidents/{incident_id}").json()
    assert data["status"] == "OPEN"
    assert len(data["evidence"]) == 4
    for item in data["evidence"]:
        assert set(item) == {
            "evidenceId",
            "category",
            "summary",
            "source",
            "collectedAt",
            "recordedAt",
        }
        assert item["summary"] == evidence_payload["summary"]
        assert item["source"] == evidence_payload["source"]
        assert item["collectedAt"] == "2020-01-01T15:00:00Z"
    assert data["evidence"][-1]["category"] == "BUSINESS_IMPACT"
    assert harness.client.get(f"/incidents/{other_id}").json()["evidence"] == []
    assert len(harness.service.get_evidence(incident_id)) == 4


@pytest.mark.parametrize("field", ["category", "summary", "source", "collectedAt"])
def test_missing_evidence_no_write(
    harness: Harness, incident_payload: dict[str, str], evidence_payload: dict[str, str], field: str
) -> None:
    incident_id = harness.client.post("/incidents", json=incident_payload).json()["incidentId"]
    del evidence_payload[field]
    response = harness.client.post(f"/incidents/{incident_id}/evidence", json=evidence_payload)
    assert response.status_code == 400
    assert harness.service.get_evidence(incident_id) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("category", "INVALID"),
        ("summary", " "),
        ("source", ""),
        ("collectedAt", "2020-01-01T00:00:00"),
    ],
)
def test_invalid_evidence_no_write(
    harness: Harness,
    incident_payload: dict[str, str],
    evidence_payload: dict[str, str],
    field: str,
    value: str,
) -> None:
    incident_id = harness.client.post("/incidents", json=incident_payload).json()["incidentId"]
    evidence_payload[field] = value
    assert (
        harness.client.post(f"/incidents/{incident_id}/evidence", json=evidence_payload).status_code
        == 400
    )
    assert harness.service.get_evidence(incident_id) == []


def test_unknown_parent(harness: Harness, evidence_payload: dict[str, str]) -> None:
    response = harness.client.post("/incidents/unknown/evidence", json=evidence_payload)
    assert response.status_code == 404
    assert set(response.json()) == {"error", "message"}
    assert harness.repository.incidents == {}


@pytest.mark.parametrize("body", ["{", "{}", "null", '"invalid body"'])
def test_unknown_parent_precedes_body_validation(harness: Harness, body: str) -> None:
    response = harness.client.post(
        "/incidents/unknown/evidence", content=body, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 404
    assert harness.repository.incidents == {}


@pytest.mark.parametrize("body", ["{", "{}", "null", '"invalid body"'])
def test_invalid_body_for_existing_parent(
    harness: Harness, incident_payload: dict[str, str], body: str
) -> None:
    incident_id = harness.client.post("/incidents", json=incident_payload).json()["incidentId"]
    response = harness.client.post(
        f"/incidents/{incident_id}/evidence",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert set(response.json()) == {"error", "message"}
    assert harness.service.get_evidence(incident_id) == []


def test_evidence_error_names_field(
    harness: Harness, incident_payload: dict[str, str], evidence_payload: dict[str, str]
) -> None:
    incident_id = harness.client.post("/incidents", json=incident_payload).json()["incidentId"]
    del evidence_payload["collectedAt"]
    response = harness.client.post(f"/incidents/{incident_id}/evidence", json=evidence_payload)
    assert response.status_code == 400
    assert "collectedAt" in response.json()["message"]


def test_evidence_request_schema_in_openapi(harness: Harness) -> None:
    spec = harness.client.get("/openapi.json").json()
    schema = spec["paths"]["/incidents/{incidentId}/evidence"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert set(schema["required"]) == {"category", "summary", "source", "collectedAt"}
    assert schema["properties"]["category"]["enum"] == [
        "TECHNICAL",
        "BUSINESS_IMPACT",
        "LEGAL",
        "OTHER",
    ]
