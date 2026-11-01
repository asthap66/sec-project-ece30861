"""REQ-04/05/08/09/10. Contract evidence and unresolved assertions: docs/phase4/."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from tests.acceptance.assertions import assert_error_body, assert_names_field, assert_utc_instant
from tests.acceptance.client import ApiClient, Auth
from tests.acceptance.test_ac01_05_incidents_evidence import attach, create_incident, get_incident
from tests.fixtures.data import VALID_EVIDENCE

pytestmark = [
    pytest.mark.acceptance,
    pytest.mark.phase4,
    pytest.mark.usefixtures("require_api_key"),
]
CALENDAR = json.loads(
    (Path(__file__).parents[1] / "fixtures/data/phase4_deadlines.json").read_text()
)


def setup_decision(api: ApiClient) -> tuple[str, dict[str, Any]]:
    incident = create_incident(api)
    evidence = attach(api, incident, VALID_EVIDENCE[0])
    return incident, {
        "decision": "MATERIAL",
        "determinedAt": "2025-09-29T12:00:00-04:00",
        "decidedBy": "Synthetic disclosure committee",
        "rationale": "Human assessment of synthetic impact",
        "evidenceIds": [evidence["evidenceId"]],
    }


@pytest.mark.parametrize("case", CALENDAR, ids=[c["name"] for c in CALENDAR])
def test_ac09_material_decision_calendar(api: ApiClient, case: dict[str, Any]) -> None:
    incident, payload = setup_decision(api)
    payload["determinedAt"] = case["determinedAt"]
    response = api.post(f"/incidents/{incident}/decisions", json=payload)
    assert response.status_code == 201, response.text
    made = response.json()
    assert isinstance(made["decisionId"], str) and made["decisionId"]
    assert made["status"] == "MATERIAL_PENDING_FILING"
    assert made["deadline"] == case["deadline"]
    stored = get_incident(api, incident)
    assert stored["status"] == made["status"]
    current = stored["currentDecision"]
    assert current["decisionId"] == made["decisionId"]
    assert current["deadline"] == case["deadline"]
    for field in ("decision", "decidedBy", "rationale", "evidenceIds"):
        assert current[field] == payload[field]
    assert_utc_instant(current["determinedAt"], payload["determinedAt"])


INVALID = [
    (f"missing-{f}", f, None)
    for f in ("decision", "determinedAt", "decidedBy", "rationale", "evidenceIds")
] + [
    ("invalid-enum", "decision", "PROBABLY_MATERIAL"),
    ("empty-reviewer", "decidedBy", ""),
    ("empty-rationale", "rationale", ""),
    ("invalid-type", "decision", 42),
    ("invalid-time", "determinedAt", "yesterday"),
    ("offset-free", "determinedAt", "2025-09-29T12:00:00"),
    ("before-discovery", "determinedAt", "1900-01-01T00:00:00Z"),
    ("empty-evidence", "evidenceIds", []),
    ("unknown-evidence", "evidenceIds", ["EVD-does-not-exist"]),
    ("evidence-wrong-type", "evidenceIds", "EVD-invalid"),
    ("reviewer-wrong-type", "decidedBy", []),
    ("rationale-wrong-type", "rationale", {}),
]


@pytest.mark.parametrize("name,field,value", INVALID, ids=[c[0] for c in INVALID])
def test_ac06_invalid_decision_no_observable_write(
    api: ApiClient, name: str, field: str, value: Any
) -> None:
    incident, payload = setup_decision(api)
    before = get_incident(api, incident)
    if name.startswith("missing-"):
        del payload[field]
    else:
        payload[field] = value
    error = assert_error_body(api.post(f"/incidents/{incident}/decisions", json=payload), 400)
    assert_names_field(error, field)
    if name == "invalid-enum":
        assert error["error"] == "INVALID_DECISION"
        assert error["message"] == "decision must be MATERIAL or NOT_MATERIAL"
    assert get_incident(api, incident) == before


@pytest.mark.parametrize("kind", ["future", "foreign", "mixed"])
def test_ac06_invalid_references_and_future(api: ApiClient, kind: str) -> None:
    incident, payload = setup_decision(api)
    if kind == "future":
        payload["determinedAt"] = (datetime.now(UTC) + timedelta(days=365)).isoformat()
    else:
        _, other = setup_decision(api)
        payload["evidenceIds"] = (
            other["evidenceIds"]
            if kind == "foreign"
            else (payload["evidenceIds"] + other["evidenceIds"])
        )
    before = get_incident(api, incident)
    assert_error_body(api.post(f"/incidents/{incident}/decisions", json=payload), 400)
    assert get_incident(api, incident) == before


def test_ac15_second_ordinary_decision_preserves_original(api: ApiClient) -> None:
    incident, payload = setup_decision(api)
    assert api.post(f"/incidents/{incident}/decisions", json=payload).status_code == 201
    before = get_incident(api, incident)
    payload["rationale"] = "Second human assessment"
    assert_error_body(api.post(f"/incidents/{incident}/decisions", json=payload), 409)
    assert get_incident(api, incident) == before


def test_ac07_evidence_does_not_decide(api: ApiClient) -> None:
    incident = create_incident(api)
    evidence = dict(VALID_EVIDENCE[0].body)
    evidence["summary"] = "Synthetic catastrophic outage and severe financial loss"
    assert api.post(f"/incidents/{incident}/evidence", json=evidence).status_code == 201
    stored = get_incident(api, incident)
    assert stored["status"] == "OPEN"
    assert stored["currentDecision"] is None
    response = api.get(
        f"/incidents/{incident}/deadline-status", params={"as_of": "2025-10-06T12:00:00Z"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "NOT_APPLICABLE"
    assert response.json()["deadline"] is None


@pytest.mark.parametrize(
    "as_of,status",
    [
        ("2025-09-30T12:00:00-04:00", "PENDING"),
        ("2025-10-06T12:00:00-04:00", "OVERDUE"),
    ],
)
def test_ac11_deadline_status_without_filing(api: ApiClient, as_of: str, status: str) -> None:
    incident, payload = setup_decision(api)
    assert api.post(f"/incidents/{incident}/decisions", json=payload).status_code == 201
    response = api.get(f"/incidents/{incident}/deadline-status", params={"as_of": as_of})
    assert response.status_code == 200, response.text
    assert response.json()["status"] == status


@pytest.mark.parametrize("operation", ["decisions", "deadline-status"])
@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG])
def test_ac14_phase4_authentication(api: ApiClient, operation: str, auth: Auth) -> None:
    method = "POST" if operation == "decisions" else "GET"
    assert_error_body(api.request(method, f"/incidents/INC-unknown/{operation}", auth=auth), 401)


@pytest.mark.parametrize("operation", ["decisions", "deadline-status"])
def test_ac03_phase4_unknown_incident(api: ApiClient, operation: str) -> None:
    _, payload = setup_decision(api)
    method = "POST" if operation == "decisions" else "GET"
    path = f"/incidents/INC-unknown/{operation}"
    response = api.post(path, json=payload) if method == "POST" else api.get(path)
    assert_error_body(response, 404)


def test_ac06_not_material_has_no_applicable_deadline(api: ApiClient) -> None:
    """Q3.2 Model 1 and Q5.2 define state and null decision deadline."""
    incident, payload = setup_decision(api)
    payload["decision"] = "NOT_MATERIAL"
    response = api.post(f"/incidents/{incident}/decisions", json=payload)
    assert response.status_code == 201, response.text
    made = response.json()
    assert isinstance(made["decisionId"], str) and made["decisionId"]
    detail = get_incident(api, incident)
    assert detail["status"] == made["status"] == "NOT_MATERIAL"
    assert made["deadline"] is None
    stored = detail["currentDecision"]
    assert stored["deadline"] is None
    for field in ("decidedBy", "rationale", "evidenceIds"):
        assert stored[field] == payload[field]
    assert_utc_instant(stored["determinedAt"], payload["determinedAt"])
    assert stored["decisionId"] == made["decisionId"]
    assert stored["decision"] == "NOT_MATERIAL"
    status = api.get(
        f"/incidents/{incident}/deadline-status", params={"as_of": "2025-10-06T12:00:00Z"}
    )
    assert status.status_code == 200, status.text
    assert status.json()["status"] == "NOT_APPLICABLE"
    assert status.json()["deadline"] is None


def test_ac16_reset_removes_decided_incident(api: ApiClient, allow_destructive: None) -> None:
    incident, payload = setup_decision(api)
    assert api.post(f"/incidents/{incident}/decisions", json=payload).status_code == 201
    reset = api.post("/reset")
    assert reset.status_code == 200, reset.text
    assert reset.json()["status"] == "RESET_COMPLETE"
    assert_error_body(api.get(f"/incidents/{incident}"), 404)
    assert get_incident(api, create_incident(api))["currentDecision"] is None


def test_ac15_material_decision_after_not_material(api: ApiClient) -> None:
    """Model 1 explicitly allows NOT_MATERIAL -> MATERIAL_PENDING_FILING."""
    incident, payload = setup_decision(api)
    payload["decision"] = "NOT_MATERIAL"
    first = api.post(f"/incidents/{incident}/decisions", json=payload)
    assert first.status_code == 201, first.text
    assert get_incident(api, incident)["status"] == "NOT_MATERIAL"
    payload["decision"] = "MATERIAL"
    second = api.post(f"/incidents/{incident}/decisions", json=payload)
    assert second.status_code == 201, second.text
    made = second.json()
    assert made["decisionId"] != first.json()["decisionId"]
    assert made["status"] == "MATERIAL_PENDING_FILING"
    assert made["deadline"] == "2025-10-03"
    detail = get_incident(api, incident)
    assert detail["status"] == made["status"]
    assert detail["currentDecision"]["decisionId"] == made["decisionId"]


@pytest.mark.parametrize(
    "as_of,status,days",
    [
        ("2026-10-01T12:00:00-04:00", "PENDING", 1),
        ("2026-10-05T12:00:00-04:00", "OVERDUE", 1),
        ("2026-10-06T12:00:00-04:00", "OVERDUE", 2),
    ],
)
def test_ac11_model3_business_days(api: ApiClient, as_of: str, status: str, days: int) -> None:
    """Model 3 gives these exact counts, independently of calculator code."""
    incident, payload = setup_decision(api)
    payload["determinedAt"] = "2026-09-28T10:00:00-04:00"
    response = api.post(f"/incidents/{incident}/decisions", json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["deadline"] == "2026-10-02"
    response = api.get(f"/incidents/{incident}/deadline-status", params={"as_of": as_of})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["deadline"] == "2026-10-02"
    assert body["status"] == status
    assert type(body["businessDays"]) is int
    assert body["businessDays"] == days


@pytest.mark.parametrize(
    "as_of,status",
    [
        ("2025-10-04T03:59:59Z", "PENDING"),
        ("2025-10-04T00:00:00-04:00", "OVERDUE"),
    ],
)
def test_ac11_eastern_due_date_boundary(api: ApiClient, as_of: str, status: str) -> None:
    """Model 3 compares Eastern calendar dates, including the entire due date."""
    incident, payload = setup_decision(api)
    response = api.post(f"/incidents/{incident}/decisions", json=payload)
    assert response.status_code == 201, response.text
    response = api.get(f"/incidents/{incident}/deadline-status", params={"as_of": as_of})
    assert response.status_code == 200, response.text
    assert response.json()["status"] == status
    assert response.json()["deadline"] == "2025-10-03"
