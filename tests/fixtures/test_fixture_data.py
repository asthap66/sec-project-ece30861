"""Self-checks on the shared JSON fixtures (no service needed; runs in CI).

These keep the fixture files consistent with the pod contract's field rules
(Phase 2 - Pod.pdf, Q5.2) so a typo in the data can't masquerade as a server bug.
"""

from datetime import UTC, datetime

import pytest

from tests.fixtures.data import (
    INVALID_EVIDENCE,
    INVALID_INCIDENTS,
    VALID_EVIDENCE,
    VALID_INCIDENTS,
    Case,
    unknown_incident_ids,
)
from tests.fixtures.synthetic import EVIDENCE_CATEGORIES

INCIDENT_FIELDS = {"title", "description", "discoveredAt", "reporterName"}
EVIDENCE_FIELDS = {"category", "summary", "source", "collectedAt"}


def _aware(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    assert parsed.tzinfo is not None, f"{value} has no timezone offset"
    return parsed


def _utc_z(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _ids(cases: list[Case]) -> list[str]:
    return [c.name for c in cases]


def test_case_names_are_unique() -> None:
    for cases in (VALID_INCIDENTS, INVALID_INCIDENTS, VALID_EVIDENCE, INVALID_EVIDENCE):
        assert len(set(_ids(cases))) == len(cases)


@pytest.mark.parametrize("case", VALID_INCIDENTS, ids=_ids(VALID_INCIDENTS))
def test_valid_incident_follows_contract(case: Case) -> None:
    assert set(case.body) == INCIDENT_FIELDS
    assert all(isinstance(case.body[f], str) and case.body[f] for f in INCIDENT_FIELDS)
    discovered = _aware(case.body["discoveredAt"])
    assert discovered < datetime.now(UTC)
    assert case.expected["status"] == "OPEN"
    assert case.expected["discoveredAt"] == _utc_z(discovered)


@pytest.mark.parametrize("case", VALID_EVIDENCE, ids=_ids(VALID_EVIDENCE))
def test_valid_evidence_follows_contract(case: Case) -> None:
    assert set(case.body) == EVIDENCE_FIELDS
    assert case.body["category"] in EVIDENCE_CATEGORIES
    assert case.body["summary"] and case.body["source"]
    assert case.expected["collectedAt"] == _utc_z(_aware(case.body["collectedAt"]))


def test_valid_evidence_covers_every_category_and_ac04() -> None:
    categories = [c.body["category"] for c in VALID_EVIDENCE]
    assert set(categories) == set(EVIDENCE_CATEGORIES)
    assert categories.count("TECHNICAL") >= 3  # AC-04 attaches three TECHNICAL items


@pytest.mark.parametrize(
    ("case", "fields"),
    [(c, INCIDENT_FIELDS) for c in INVALID_INCIDENTS]
    + [(c, EVIDENCE_FIELDS) for c in INVALID_EVIDENCE],
    ids=_ids(INVALID_INCIDENTS) + _ids(INVALID_EVIDENCE),
)
def test_invalid_case_names_a_real_field(case: Case, fields: set[str]) -> None:
    assert case.expected["httpStatus"] == 400
    assert case.expected["field"] in fields
    assert set(case.body) <= fields


def test_ac02_cases_are_present() -> None:
    names = set(_ids(INVALID_INCIDENTS))
    assert {
        "ac02-missing-description",
        "ac02-timestamp-without-offset",
        "ac02-future-discovery",
    } <= names


def test_unknown_ids_are_present() -> None:
    assert unknown_incident_ids()
