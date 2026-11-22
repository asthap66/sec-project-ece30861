"""Feature tests use an injected transactional test double, never production storage."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.deadline_calendar import SHARED_CALENDAR
from app.errors import ApiError
from app.schemas import (
    CorrectionCreate,
    DecisionCreate,
    EvidenceCreate,
    FilingCreate,
    FilingDetail,
    FilingTimeliness,
    IncidentCreate,
    IncidentStatus,
    IncidentTimeline,
)
from app.services.phase5 import Phase5Service
from tests.unit.decision_fakes import TestDecisionRepository, TestTransaction


class Transaction(TestTransaction):
    def append_correction(self, data: CorrectionCreate) -> str:
        return self.append_decision(data)

    def append_filing(
        self, data: FilingCreate, timeliness: FilingTimeliness, business_days_late: int
    ) -> str:
        self.repository.incidents[self.incident.incident_id].filing = FilingDetail(
            **data.model_dump(by_alias=False),
            filing_id="FIL-001",
            timeliness=timeliness,
            business_days_late=business_days_late,
        )
        self.repository.incidents[self.incident.incident_id].status = IncidentStatus.FILED
        return "FIL-001"


class Repository(TestDecisionRepository):
    @contextmanager
    def transaction(self, incident_id: str) -> Iterator[Transaction]:
        with self._lock:
            before = {k: v.model_copy(deep=True) for k, v in self.incidents.items()}
            history = [v.model_copy(deep=True) for v in self.history]
            incident = self.get_incident(incident_id)
            if incident is None:
                raise ApiError(404, "NOT_FOUND", "Incident not found")
            try:
                yield Transaction(self, incident)
                if self.fail_commit:
                    raise RuntimeError("commit failed")
            except Exception:
                self.incidents, self.history = before, history
                raise

    def get_timeline(self, incident_id: str) -> IncidentTimeline:
        raise NotImplementedError


@pytest.fixture
def workflow(
    incident_payload: dict[str, str], evidence_payload: dict[str, str]
) -> tuple[Phase5Service, Repository]:
    repo = Repository()
    repo.create_incident(IncidentCreate.model_validate(incident_payload))
    repo.add_evidence("INC-001", EvidenceCreate.model_validate(evidence_payload))
    service = Phase5Service(repo, SHARED_CALENDAR, clock=lambda: datetime(2026, 10, 1, tzinfo=UTC))
    return service, repo


DECISION = {
    "decision": "MATERIAL",
    "determinedAt": "2025-09-29T12:00:00-04:00",
    "decidedBy": "Reviewer",
    "rationale": "Impact",
    "evidenceIds": ["EVD-001"],
}


def test_correction_preserves_original_and_changes_current(
    workflow: tuple[Phase5Service, Repository],
) -> None:
    service, repo = workflow
    first = service.record_decision("INC-001", DecisionCreate.model_validate(DECISION))
    result = service.correct_decision(
        "INC-001",
        CorrectionCreate.model_validate(
            {**DECISION, "correctsDecisionId": first.decision_id, "decision": "NOT_MATERIAL"}
        ),
    )
    assert result.status == "NOT_MATERIAL" and result.deadline is None
    assert [d.decision for d in repo.history] == ["MATERIAL", "NOT_MATERIAL"]
    current = service.get_incident("INC-001").current_decision
    assert current is not None and current.decision_id == result.decision_id


@pytest.mark.parametrize(
    "changes",
    [
        {"correctsDecisionId": "DEC-other"},
        {"evidenceIds": ["EVD-other"]},
        {"determinedAt": "1900-01-01T00:00:00Z"},
        {"determinedAt": "2099-01-01T00:00:00Z"},
    ],
)
def test_correction_rejection_does_not_write(
    workflow: tuple[Phase5Service, Repository], changes: dict[str, object]
) -> None:
    service, repo = workflow
    first = service.record_decision("INC-001", DecisionCreate.model_validate(DECISION))
    before = service.get_incident("INC-001")
    with pytest.raises(ApiError) as exc:
        service.correct_decision(
            "INC-001",
            CorrectionCreate.model_validate(
                {**DECISION, "correctsDecisionId": first.decision_id, **changes}
            ),
        )
    assert exc.value.status_code == 400
    assert len(repo.history) == 1 and service.get_incident("INC-001") == before


@pytest.mark.parametrize(
    ("filed", "timeliness", "days"),
    [
        ("2025-10-03T23:59:59-04:00", "ON_TIME", 0),
        ("2025-10-06T12:00:00-04:00", "LATE", 1),
    ],
)
def test_filing_and_conflicts(
    workflow: tuple[Phase5Service, Repository], filed: str, timeliness: str, days: int
) -> None:
    service, repo = workflow
    filing = FilingCreate.model_validate({"filedAt": filed, "accessionNumber": "example"})
    with pytest.raises(ApiError) as exc:
        service.record_filing("INC-001", filing)
    assert exc.value.status_code == 409
    decision = service.record_decision("INC-001", DecisionCreate.model_validate(DECISION))
    result = service.record_filing("INC-001", filing)
    assert (result.status, result.timeliness, result.business_days_late) == (
        "FILED",
        timeliness,
        days,
    )
    before = service.get_incident("INC-001")
    with pytest.raises(ApiError) as exc:
        service.record_filing("INC-001", filing)
    assert exc.value.status_code == 409
    with pytest.raises(ApiError) as exc:
        service.correct_decision(
            "INC-001",
            CorrectionCreate.model_validate(
                {**DECISION, "correctsDecisionId": decision.decision_id}
            ),
        )
    assert exc.value.status_code == 409
    assert service.get_incident("INC-001") == before and len(repo.history) == 1


def test_filing_schema() -> None:
    assert (
        FilingCreate.model_validate(
            {"filedAt": "2025-10-03T12:00:00-04:00", "accessionNumber": "A"}
        ).model_dump(mode="json")["filedAt"]
        == "2025-10-03T16:00:00Z"
    )
    for payload in (
        {"filedAt": "2025-10-03T12:00:00", "accessionNumber": "A"},
        {"filedAt": "2025-10-03T12:00:00Z", "accessionNumber": "  "},
    ):
        with pytest.raises(ValidationError):
            FilingCreate.model_validate(payload)


def test_missing_incident_and_failed_commit(workflow: tuple[Phase5Service, Repository]) -> None:
    service, repo = workflow
    payload = CorrectionCreate.model_validate({**DECISION, "correctsDecisionId": "DEC-001"})
    with pytest.raises(ApiError) as exc:
        service.correct_decision("missing", payload)
    assert exc.value.status_code == 404
    service.record_decision("INC-001", DecisionCreate.model_validate(DECISION))
    before = service.get_incident("INC-001")
    repo.fail_commit = True
    with pytest.raises(RuntimeError):
        service.correct_decision("INC-001", payload)
    assert len(repo.history) == 1 and service.get_incident("INC-001") == before


def test_phase5_routes_require_auth_and_use_the_integrated_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    from app.config import get_settings
    from app.main import create_app

    monkeypatch.setenv("API_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost/test")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            for method, path in (
                ("POST", "/incidents/INC-001/corrections"),
                ("POST", "/incidents/INC-001/filing"),
                ("GET", "/incidents/INC-001/timeline"),
            ):
                assert client.request(method, path).status_code == 401
                assert (
                    client.request(method, path, headers={"X-API-Key": "wrong"}).status_code == 401
                )
                if method == "POST":
                    # The persistence adapter is integrated: a valid key reaches
                    # request validation instead of the old 503 placeholder.
                    response = client.request(method, path, headers={"X-API-Key": "test-secret"})
                    assert response.status_code == 400
                    assert response.json()["error"] != "PHASE5_DEPENDENCIES_UNAVAILABLE"
    finally:
        get_settings.cache_clear()
