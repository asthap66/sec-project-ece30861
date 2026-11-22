"""Phase 5 black-box contract checks; require the integrated storage adapter.

The public shapes come from docs/phase5/astha-api-handoff.md. These tests do
not import production schemas, services, or calendar code for expected values.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from tests.acceptance.assertions import assert_error_body, assert_names_field, assert_utc_instant
from tests.acceptance.client import ApiClient, Auth
from tests.acceptance.test_ac01_05_incidents_evidence import get_incident
from tests.acceptance.test_phase4_decisions import create_phase4_incident, setup_decision

pytestmark = [
    pytest.mark.acceptance,
    pytest.mark.phase5,
    pytest.mark.usefixtures("require_api_key"),
]
SCENARIOS = json.loads(
    (Path(__file__).parents[1] / "fixtures/data/phase5_scenarios.json").read_text()
)


def _material(api: ApiClient) -> tuple[str, dict[str, Any], str]:
    incident, payload = setup_decision(api)
    response = api.post(f"/incidents/{incident}/decisions", json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["deadline"] == SCENARIOS["incident"]["deadline"]
    return incident, payload, str(response.json()["decisionId"])


def _correction(payload: dict[str, Any], decision_id: str) -> dict[str, Any]:
    return {
        **payload,
        "correctsDecisionId": decision_id,
        "decision": SCENARIOS["incident"]["correctedDecision"]["decision"],
        "determinedAt": SCENARIOS["incident"]["correctedDecision"]["determinedAt"],
        "rationale": SCENARIOS["incident"]["correctedDecision"]["rationale"],
    }


def _timeline(api: ApiClient, incident: str) -> dict[str, Any]:
    response = api.get(f"/incidents/{incident}/timeline")
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    assert body["incidentId"] == incident
    return body


def test_ac08_correction_retains_original_decision(api: ApiClient) -> None:
    incident, payload, original_id = _material(api)
    response = api.post(
        f"/incidents/{incident}/corrections", json=_correction(payload, original_id)
    )
    assert response.status_code == 201, response.text
    made = response.json()
    assert isinstance(made["decisionId"], str) and made["decisionId"] != original_id
    assert made["status"] == "NOT_MATERIAL"
    assert made["deadline"] is None
    detail = get_incident(api, incident)
    assert detail["status"] == "NOT_MATERIAL"
    assert detail["currentDecision"]["decisionId"] == made["decisionId"]
    assert detail["currentDecision"]["decision"] == "NOT_MATERIAL"
    assert_utc_instant(
        detail["currentDecision"]["determinedAt"],
        SCENARIOS["incident"]["correctedDecision"]["determinedAt"],
    )
    events = _timeline(api, incident)["events"]
    assert ("DECISION_RECORDED", original_id) in [
        (event["eventType"], event["referenceId"]) for event in events
    ]
    assert ("DECISION_CORRECTED", made["decisionId"]) in [
        (event["eventType"], event["referenceId"]) for event in events
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("evidenceIds", ["EVD-unknown"]),
        ("determinedAt", "1900-01-01T00:00:00Z"),
        ("determinedAt", "2099-01-01T00:00:00Z"),
        ("decision", "PROBABLY_MATERIAL"),
    ],
)
def test_ac08_invalid_correction_preserves_state(api: ApiClient, field: str, value: object) -> None:
    incident, payload, original_id = _material(api)
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    bad = _correction(payload, original_id)
    bad[field] = value
    error = assert_error_body(api.post(f"/incidents/{incident}/corrections", json=bad), 400)
    assert_names_field(error, field)
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


def test_ac08_stale_correction_reference_is_rejected(api: ApiClient) -> None:
    """The shared contract has not fixed whether this is 400 or 409."""
    incident, payload, original_id = _material(api)
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    bad = _correction(payload, original_id)
    bad["correctsDecisionId"] = "DEC-unknown"
    response = api.post(f"/incidents/{incident}/corrections", json=bad)
    assert response.status_code in (400, 409), response.text
    error = assert_error_body(response, response.status_code)
    assert_names_field(error, "correctsDecisionId")
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


@pytest.mark.parametrize("field", ["correctsDecisionId", "evidenceIds", "rationale"])
def test_ac08_missing_correction_field_preserves_state(api: ApiClient, field: str) -> None:
    incident, payload, original_id = _material(api)
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    bad = _correction(payload, original_id)
    del bad[field]
    error = assert_error_body(api.post(f"/incidents/{incident}/corrections", json=bad), 400)
    assert_names_field(error, field)
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


def test_ac08_foreign_evidence_cannot_support_correction(api: ApiClient) -> None:
    incident, payload, original_id = _material(api)
    _, other_payload = setup_decision(api)
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    bad = _correction(payload, original_id)
    bad["evidenceIds"] = other_payload["evidenceIds"]
    error = assert_error_body(api.post(f"/incidents/{incident}/corrections", json=bad), 400)
    assert_names_field(error, "evidenceIds")
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


def test_ac08_unknown_incident_correction_is_404(api: ApiClient) -> None:
    _, payload, decision_id = _material(api)
    error = api.post("/incidents/INC-unknown/corrections", json=_correction(payload, decision_id))
    assert_error_body(error, 404)


@pytest.mark.parametrize(
    "case", SCENARIOS["filingCases"], ids=[case["name"] for case in SCENARIOS["filingCases"]]
)
def test_ac11_filing_boundary_and_stored_detail(api: ApiClient, case: dict[str, Any]) -> None:
    incident, _, _ = _material(api)
    request = {"filedAt": case["filedAt"], "accessionNumber": f"synthetic-{case['name']}"}
    response = api.post(f"/incidents/{incident}/filing", json=request)
    assert response.status_code == 201, response.text
    made = response.json()
    assert isinstance(made["filingId"], str) and made["filingId"]
    assert made["status"] == "FILED"
    assert made["timeliness"] == case["timeliness"]
    assert type(made["businessDaysLate"]) is int
    assert made["businessDaysLate"] == case["businessDaysLate"]
    detail = get_incident(api, incident)
    assert detail["status"] == "FILED"
    filing = detail["filing"]
    assert filing["filingId"] == made["filingId"]
    assert filing["accessionNumber"] == request["accessionNumber"]
    assert filing["timeliness"] == made["timeliness"]
    assert filing["businessDaysLate"] == made["businessDaysLate"]
    assert_utc_instant(filing["filedAt"], request["filedAt"])


@pytest.mark.parametrize("state", ["OPEN", "NOT_MATERIAL"])
def test_ac15_filing_requires_material_decision(api: ApiClient, state: str) -> None:
    incident, payload = setup_decision(api)
    if state == "NOT_MATERIAL":
        payload["decision"] = "NOT_MATERIAL"
        assert api.post(f"/incidents/{incident}/decisions", json=payload).status_code == 201
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    request = {"filedAt": "2025-10-02T12:00:00-04:00", "accessionNumber": "synthetic"}
    assert_error_body(api.post(f"/incidents/{incident}/filing", json=request), 409)
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


def test_ac15_duplicate_filing_is_conflict(api: ApiClient) -> None:
    incident, _, _ = _material(api)
    request = {"filedAt": "2025-10-02T12:00:00-04:00", "accessionNumber": "synthetic"}
    first = api.post(f"/incidents/{incident}/filing", json=request)
    assert first.status_code == 201, first.text
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    assert_error_body(api.post(f"/incidents/{incident}/filing", json=request), 409)
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


def test_ac15_correction_after_filing_is_conflict(api: ApiClient) -> None:
    incident, payload, original_id = _material(api)
    filing = api.post(
        f"/incidents/{incident}/filing",
        json={"filedAt": "2025-10-02T12:00:00-04:00", "accessionNumber": "synthetic"},
    )
    assert filing.status_code == 201, filing.text
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    assert_error_body(
        api.post(f"/incidents/{incident}/corrections", json=_correction(payload, original_id)),
        409,
    )
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


@pytest.mark.parametrize(
    "field,value",
    [
        ("filedAt", "2025-10-02T12:00:00"),
        ("filedAt", "not-a-time"),
        ("accessionNumber", "  "),
    ],
)
def test_ac11_malformed_filing_is_rejected(api: ApiClient, field: str, value: object) -> None:
    incident, _, _ = _material(api)
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    request: dict[str, object] = {
        "filedAt": "2025-10-02T12:00:00-04:00",
        "accessionNumber": "synthetic",
    }
    request[field] = value
    error = assert_error_body(api.post(f"/incidents/{incident}/filing", json=request), 400)
    assert_names_field(error, field)
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


@pytest.mark.parametrize("field", ["filedAt", "accessionNumber"])
def test_ac11_missing_filing_field_is_rejected(api: ApiClient, field: str) -> None:
    incident, _, _ = _material(api)
    before = get_incident(api, incident)
    history = _timeline(api, incident)
    request = {"filedAt": "2025-10-02T12:00:00-04:00", "accessionNumber": "synthetic"}
    del request[field]
    error = assert_error_body(api.post(f"/incidents/{incident}/filing", json=request), 400)
    assert_names_field(error, field)
    assert get_incident(api, incident) == before
    assert _timeline(api, incident) == history


def test_ac11_unknown_incident_filing_is_404(api: ApiClient) -> None:
    request = {"filedAt": "2025-10-02T12:00:00-04:00", "accessionNumber": "synthetic"}
    assert_error_body(api.post("/incidents/INC-unknown/filing", json=request), 404)


def test_ac12_timeline_complete_ordered_and_recording_timestamps(api: ApiClient) -> None:
    incident, payload, original_id = _material(api)
    evidence_id = payload["evidenceIds"][0]
    correction = _correction(payload, original_id)
    correction["decision"] = "MATERIAL"
    response = api.post(f"/incidents/{incident}/corrections", json=correction)
    assert response.status_code == 201, response.text
    corrected_id = response.json()["decisionId"]
    filing = api.post(
        f"/incidents/{incident}/filing",
        json={"filedAt": "2025-10-02T12:00:00-04:00", "accessionNumber": "synthetic"},
    )
    assert filing.status_code == 201, filing.text
    filed_id = filing.json()["filingId"]
    body = _timeline(api, incident)
    events = body["events"]
    assert [(event["eventType"], event["referenceId"]) for event in events] == [
        ("INCIDENT_CREATED", incident),
        ("EVIDENCE_ADDED", evidence_id),
        ("DECISION_RECORDED", original_id),
        ("DECISION_CORRECTED", corrected_id),
        ("FILING_RECORDED", filed_id),
    ]
    recorded = [datetime.fromisoformat(event["recordedAt"]) for event in events]
    assert all(moment.utcoffset() == timedelta(0) for moment in recorded)
    assert recorded == sorted(recorded)
    assert body["evidenceCounts"] == {
        "technical": 0,
        "businessImpact": 1,
        "legal": 0,
        "other": 0,
    }
    duration = body["discoveryToDeterminationDays"]
    assert isinstance(duration, (float, int)) and duration >= 0
    assert get_incident(api, incident)["currentDecision"]["decisionId"] == corrected_id


def test_ac12_empty_timeline_and_unknown_incident(api: ApiClient) -> None:
    incident = create_phase4_incident(api)
    body = _timeline(api, incident)
    assert [(event["eventType"], event["referenceId"]) for event in body["events"]] == [
        ("INCIDENT_CREATED", incident)
    ]
    assert body["evidenceCounts"] == {
        "technical": 0,
        "businessImpact": 0,
        "legal": 0,
        "other": 0,
    }
    assert body["discoveryToDeterminationDays"] is None
    assert_error_body(api.get("/incidents/INC-unknown/timeline"), 404)


@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG])
@pytest.mark.parametrize("operation", ["corrections", "filing", "timeline"])
def test_ac14_phase5_routes_require_key(api: ApiClient, auth: Auth, operation: str) -> None:
    method = "GET" if operation == "timeline" else "POST"
    assert_error_body(api.request(method, f"/incidents/INC-unknown/{operation}", auth=auth), 401)
