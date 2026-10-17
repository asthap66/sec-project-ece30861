"""AC-01 to AC-05: incident create/retrieve, rejection, unknown IDs, evidence.

Driven by the shared JSON fixtures in tests/fixtures/data/. Writes synthetic
incidents to the target but never resets it, so these are not destructive.

AC-02's "incident count is unchanged" needs a list route (docs/contract-issues.md
#2). Until then, rejected evidence is checked by re-reading the parent incident.
"""

from typing import Any

import pytest

from tests.acceptance.assertions import assert_error_body, assert_names_field, assert_utc_instant
from tests.acceptance.client import ApiClient
from tests.fixtures.data import (
    INVALID_EVIDENCE,
    INVALID_INCIDENTS,
    VALID_EVIDENCE,
    VALID_INCIDENTS,
    Case,
    unknown_incident_ids,
)

pytestmark = [pytest.mark.acceptance, pytest.mark.usefixtures("require_api_key")]

INCIDENT_TEXT_FIELDS = ("title", "description", "reporterName")
EVIDENCE_TEXT_FIELDS = ("category", "summary", "source")


def _ids(cases: list[Case]) -> list[str]:
    return [c.name for c in cases]


def _evidence(name: str) -> Case:
    return next(c for c in VALID_EVIDENCE if c.name == name)


def create_incident(api: ApiClient, case: Case = VALID_INCIDENTS[0]) -> str:
    response = api.post("/incidents", json=case.body)
    assert response.status_code == 201, response.text
    body = response.json()
    assert isinstance(body.get("incidentId"), str) and body["incidentId"]
    assert body.get("status") == "OPEN"
    return str(body["incidentId"])


def get_incident(api: ApiClient, incident_id: str) -> dict[str, Any]:
    response = api.get(f"/incidents/{incident_id}")
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


def attach(api: ApiClient, incident_id: str, case: Case) -> dict[str, Any]:
    response = api.post(f"/incidents/{incident_id}/evidence", json=case.body)
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    assert isinstance(body.get("evidenceId"), str) and body["evidenceId"]
    assert isinstance(body.get("recordedAt"), str)
    assert_utc_instant(body["recordedAt"], body["recordedAt"])
    return body


def assert_evidence_matches(stored: dict[str, Any], case: Case, created: dict[str, Any]) -> None:
    assert stored["evidenceId"] == created["evidenceId"]
    for field in EVIDENCE_TEXT_FIELDS:
        assert stored[field] == case.body[field], field
    assert_utc_instant(stored["collectedAt"], case.expected["collectedAt"])
    assert_utc_instant(stored["recordedAt"], created["recordedAt"])


# AC-01 ---------------------------------------------------------------------


@pytest.mark.parametrize("case", VALID_INCIDENTS, ids=_ids(VALID_INCIDENTS))
def test_ac01_create_then_retrieve_returns_identical_values(api: ApiClient, case: Case) -> None:
    incident_id = create_incident(api, case)

    body = get_incident(api, incident_id)

    assert body["incidentId"] == incident_id
    for field in INCIDENT_TEXT_FIELDS:
        assert body[field] == case.body[field], field
    assert_utc_instant(body["discoveredAt"], case.expected["discoveredAt"])
    assert body["status"] == case.expected["status"]
    assert body["evidence"] == []
    assert body["currentDecision"] is None
    assert body["filing"] is None


def test_ac01_each_incident_gets_a_distinct_id(api: ApiClient) -> None:
    assert create_incident(api) != create_incident(api)


# AC-02 ---------------------------------------------------------------------


@pytest.mark.parametrize("case", INVALID_INCIDENTS, ids=_ids(INVALID_INCIDENTS))
def test_ac02_invalid_incident_is_rejected_naming_the_field(api: ApiClient, case: Case) -> None:
    body = assert_error_body(api.post("/incidents", json=case.body), 400)
    assert_names_field(body, case.expected["field"])


# AC-03 ---------------------------------------------------------------------


@pytest.mark.parametrize("incident_id", unknown_incident_ids())
def test_ac03_unknown_id_get_and_post_return_404(api: ApiClient, incident_id: str) -> None:
    assert_error_body(api.get(f"/incidents/{incident_id}"), 404)
    response = api.post(f"/incidents/{incident_id}/evidence", json=VALID_EVIDENCE[0].body)
    assert_error_body(response, 404)


# AC-04 ---------------------------------------------------------------------


def test_ac04_three_technical_items_are_linked_to_the_incident(api: ApiClient) -> None:
    incident_id = create_incident(api)
    cases = [_evidence(f"ac04-technical-{n}") for n in (1, 2, 3)]
    created = [attach(api, incident_id, case) for case in cases]
    assert len({c["evidenceId"] for c in created}) == 3

    stored = {e["evidenceId"]: e for e in get_incident(api, incident_id)["evidence"]}

    assert set(stored) == {c["evidenceId"] for c in created}
    for case, made in zip(cases, created, strict=True):
        assert_evidence_matches(stored[made["evidenceId"]], case, made)

    unknown = unknown_incident_ids()[0]
    assert_error_body(api.post(f"/incidents/{unknown}/evidence", json=cases[0].body), 404)


def test_ac04_evidence_is_not_shared_between_incidents(api: ApiClient) -> None:
    first, second = create_incident(api), create_incident(api)
    attach(api, first, _evidence("ac04-technical-1"))

    assert get_incident(api, second)["evidence"] == []


# AC-05 and the other categories --------------------------------------------


@pytest.mark.parametrize("case", VALID_EVIDENCE, ids=_ids(VALID_EVIDENCE))
def test_ac05_evidence_is_stored_and_returned_unchanged(api: ApiClient, case: Case) -> None:
    incident_id = create_incident(api)
    created = attach(api, incident_id, case)

    (stored,) = get_incident(api, incident_id)["evidence"]

    assert_evidence_matches(stored, case, created)


@pytest.mark.parametrize("case", INVALID_EVIDENCE, ids=_ids(INVALID_EVIDENCE))
def test_invalid_evidence_is_rejected_and_not_attached(api: ApiClient, case: Case) -> None:
    incident_id = create_incident(api)

    body = assert_error_body(api.post(f"/incidents/{incident_id}/evidence", json=case.body), 400)

    assert_names_field(body, case.expected["field"])
    assert get_incident(api, incident_id)["evidence"] == []


# Append-only (contract Q5.1: edit/delete attempts return 405) --------------


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_stored_incident_cannot_be_edited_or_deleted(api: ApiClient, method: str) -> None:
    incident_id = create_incident(api)

    assert_error_body(api.request(method, f"/incidents/{incident_id}", json={}), 405)

    assert get_incident(api, incident_id)["title"] == VALID_INCIDENTS[0].body["title"]
