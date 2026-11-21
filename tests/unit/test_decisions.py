"""Astha's Phase 4 feature tests with injected storage, calendar and clock."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from app.errors import ApiError
from app.schemas import DecisionCreate, IncidentCreate, IncidentStatus
from app.services.decisions import DecisionService
from tests.unit.decision_fakes import StubCalendar, TestDecisionRepository

NOW = datetime(2026, 10, 1, tzinfo=UTC)
PAYLOAD: dict[str, Any] = {
    "decision": "MATERIAL",
    "determinedAt": "2025-09-29T12:00:00-04:00",
    "decidedBy": " Human reviewer ",
    "rationale": " Human assessment ",
    "evidenceIds": ["EVD-001"],
}


@pytest.fixture
def workflow(
    incident_payload: dict[str, str], evidence_payload: dict[str, str]
) -> tuple[DecisionService, TestDecisionRepository, StubCalendar]:
    from app.schemas import EvidenceCreate

    repository = TestDecisionRepository()
    incident = repository.create_incident(IncidentCreate.model_validate(incident_payload))
    repository.add_evidence(incident.incident_id, EvidenceCreate.model_validate(evidence_payload))
    calendar = StubCalendar()
    return DecisionService(repository, calendar, clock=lambda: NOW), repository, calendar


@pytest.mark.parametrize("field", list(PAYLOAD))
def test_required_decision_fields(field: str) -> None:
    data = dict(PAYLOAD)
    del data[field]
    with pytest.raises(ValidationError):
        DecisionCreate.model_validate(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("decision", "material"),
        ("decision", 42),
        ("decision", {}),
        ("decidedBy", " \t"),
        ("decidedBy", 4),
        ("rationale", ""),
        ("rationale", {}),
        ("evidenceIds", []),
        ("evidenceIds", "EVD-001"),
        ("evidenceIds", [4]),
        ("evidenceIds", [" "]),
        ("evidenceIds", [None]),
        ("determinedAt", "2025-09-29T12:00:00"),
        ("determinedAt", 123),
        ("determinedAt", "2025-09-29 12:00:00Z"),
        ("determinedAt", None),
    ],
)
def test_invalid_decision_schema(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        DecisionCreate.model_validate({**PAYLOAD, field: value})


def test_schema_preserves_text_and_utc() -> None:
    data = DecisionCreate.model_validate(PAYLOAD).model_dump(mode="json")
    assert data == {**PAYLOAD, "determinedAt": "2025-09-29T16:00:00Z"}


def test_foreign_evidence_is_rejected(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar],
    incident_payload: dict[str, str],
    evidence_payload: dict[str, str],
) -> None:
    from app.schemas import EvidenceCreate

    service, repository, _ = workflow
    other = repository.create_incident(IncidentCreate.model_validate(incident_payload))
    evidence = repository.add_evidence(
        other.incident_id, EvidenceCreate.model_validate(evidence_payload)
    )
    for ids in ([evidence.evidence_id], ["EVD-001", evidence.evidence_id]):
        with pytest.raises(ApiError) as exc:
            service.record_decision(
                "INC-001", DecisionCreate.model_validate({**PAYLOAD, "evidenceIds": ids})
            )
        assert exc.value.status_code == 400
    assert repository.history == []


def test_material_round_trip(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar],
) -> None:
    service, repository, calendar = workflow
    result = service.record_decision("INC-001", DecisionCreate.model_validate(PAYLOAD))
    assert result.model_dump(mode="json") == {
        "decisionId": "DEC-001",
        "status": "MATERIAL_PENDING_FILING",
        "deadline": "2025-10-03",
    }
    detail = service.get_incident("INC-001")
    assert detail.status == result.status
    assert detail.current_decision is not None
    assert detail.current_decision.model_dump(mode="json") == {
        **PAYLOAD,
        "determinedAt": "2025-09-29T16:00:00Z",
        "decisionId": "DEC-001",
        "deadline": "2025-10-03",
    }
    assert detail.filing is None and len(detail.evidence) == 1
    assert all(value == datetime(2025, 9, 29, 16, tzinfo=UTC) for value in calendar.calculated)
    assert repository.history[0].deadline is None  # derived, never persisted by this service


def test_not_material_then_material(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar],
) -> None:
    service, repository, calendar = workflow
    first = service.record_decision(
        "INC-001", DecisionCreate.model_validate({**PAYLOAD, "decision": "NOT_MATERIAL"})
    )
    assert first.status == "NOT_MATERIAL" and first.deadline is None
    assert service.get_incident("INC-001").status == "NOT_MATERIAL"
    assert calendar.calculated == []
    assert service.deadline_status("INC-001").status == "NOT_APPLICABLE"
    second = service.record_decision("INC-001", DecisionCreate.model_validate(PAYLOAD))
    assert second.decision_id != first.decision_id
    assert second.status == "MATERIAL_PENDING_FILING"
    assert len(repository.history) == 2 and repository.history[0].decision == "NOT_MATERIAL"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("determinedAt", "1900-01-01T00:00:00Z"),
        ("determinedAt", "2099-01-01T00:00:00Z"),
        ("evidenceIds", ["EVD-other"]),
        ("evidenceIds", ["EVD-001", "EVD-other"]),
    ],
)
def test_domain_rejection_has_no_write(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar],
    field: str,
    value: object,
) -> None:
    service, repository, _ = workflow
    before = service.get_incident("INC-001")
    with pytest.raises(ApiError) as exc:
        service.record_decision("INC-001", DecisionCreate.model_validate({**PAYLOAD, field: value}))
    assert exc.value.status_code == 400
    assert field in exc.value.message
    assert repository.history == [] and service.get_incident("INC-001") == before


@pytest.mark.parametrize("state", ["MATERIAL_PENDING_FILING", "FILED"])
def test_state_conflict_preserves_decision(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar], state: str
) -> None:
    service, repository, _ = workflow
    service.record_decision("INC-001", DecisionCreate.model_validate(PAYLOAD))
    repository.incidents["INC-001"].status = IncidentStatus(state)
    before = service.get_incident("INC-001")
    with pytest.raises(ApiError) as exc:
        service.record_decision("INC-001", DecisionCreate.model_validate(PAYLOAD))
    assert exc.value.status_code == 409
    assert len(repository.history) == 1 and service.get_incident("INC-001") == before


@pytest.mark.parametrize("failure", ["calendar", "commit"])
def test_dependency_failure_never_reports_success(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar], failure: str
) -> None:
    service, repository, calendar = workflow
    repository.fail_commit = failure == "commit"
    calendar.fail = failure == "calendar"
    with pytest.raises(RuntimeError):
        service.record_decision("INC-001", DecisionCreate.model_validate(PAYLOAD))
    assert repository.history == []
    assert repository.incidents["INC-001"].current_decision is None


def test_deadline_delegates_explicit_and_default_time(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar],
) -> None:
    service, _, calendar = workflow
    service.record_decision("INC-001", DecisionCreate.model_validate(PAYLOAD))
    explicit = datetime(2025, 10, 1, 12, tzinfo=UTC)
    assert service.deadline_status("INC-001", explicit) == calendar.result
    service.deadline_status("INC-001")
    assert calendar.described == [(date(2025, 10, 3), explicit), (date(2025, 10, 3), NOW)]


def test_unknown_incident(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar],
) -> None:
    service, _, _ = workflow
    for operation in (
        lambda: service.get_incident("missing"),
        lambda: service.record_decision("missing", DecisionCreate.model_validate(PAYLOAD)),
    ):
        with pytest.raises(ApiError) as exc:
            operation()
        assert exc.value.status_code == 404


def test_concurrent_calls_use_transaction_state(
    workflow: tuple[DecisionService, TestDecisionRepository, StubCalendar],
) -> None:
    service, repository, _ = workflow

    def record() -> int:
        try:
            service.record_decision("INC-001", DecisionCreate.model_validate(PAYLOAD))
            return 201
        except ApiError as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(lambda _: record(), range(2))) == [201, 409]
    assert len(repository.history) == 1
