"""Injected Phase 4 test implementations. Never imported by application code."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime
from threading import RLock

from app.errors import ApiError
from app.schemas import (
    DeadlineState,
    DeadlineStatus,
    DecisionCreate,
    DecisionDetail,
    IncidentDetail,
)
from app.services.decisions import DecisionTransaction
from tests.unit.conftest import FakeRepository


class TestDecisionRepository(FakeRepository):
    __test__ = False

    def __init__(self) -> None:
        super().__init__()
        self.history: list[DecisionDetail] = []
        self.fail_commit = False
        self._lock = RLock()

    @contextmanager
    def transaction(self, incident_id: str) -> Iterator[DecisionTransaction]:
        with self._lock:
            before = {key: value.model_copy(deep=True) for key, value in self.incidents.items()}
            history = [item.model_copy(deep=True) for item in self.history]
            incident = self.get_incident(incident_id)
            if incident is None:
                raise ApiError(404, "NOT_FOUND", "Incident not found")
            try:
                yield TestTransaction(self, incident)
                if self.fail_commit:
                    raise RuntimeError("synthetic commit failure")
            except Exception:
                self.incidents = before
                self.history = history
                raise


class TestTransaction:
    __test__ = False

    def __init__(self, repository: TestDecisionRepository, incident: IncidentDetail) -> None:
        self.repository = repository
        self.incident = incident

    def append_decision(self, data: DecisionCreate) -> str:
        decision = DecisionDetail(
            **data.model_dump(by_alias=False),
            decision_id=f"DEC-{len(self.repository.history) + 1:03d}",
        )
        self.repository.history.append(decision)
        self.repository.incidents[self.incident.incident_id].current_decision = decision
        return decision.decision_id


class StubCalendar:
    """Fixed answers test delegation, not business-day arithmetic."""

    def __init__(self) -> None:
        self.calculated: list[datetime] = []
        self.described: list[tuple[date | None, datetime]] = []
        self.result = DeadlineStatus(
            status=DeadlineState.PENDING, deadline=date(2025, 10, 3), business_days=1
        )
        self.fail = False

    def calculate_deadline(self, determined_at: datetime) -> date:
        self.calculated.append(determined_at)
        if self.fail:
            raise RuntimeError("synthetic calendar failure")
        return date(2025, 10, 3)

    def describe_deadline(self, deadline: date | None, as_of: datetime) -> DeadlineStatus:
        self.described.append((deadline, as_of))
        if deadline is None:
            return DeadlineStatus(
                status=DeadlineState.NOT_APPLICABLE, deadline=None, business_days=0
            )
        return self.result
