"""Human decision workflow. Persistence and calendar implementations are injected.

The repository owns locking, commit and rollback. Its transaction must lock the
incident before reading current state and retain that lock through commit.
No SQLAlchemy mapping or holiday policy is defined in this feature module.
"""

from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import UTC, date, datetime
from typing import Protocol

from app.errors import ApiError
from app.schemas import (
    DeadlineStatus,
    DecisionCreate,
    DecisionCreated,
    IncidentDetail,
    IncidentStatus,
    MaterialityDecision,
)


class DecisionTransaction(Protocol):
    @property
    def incident(self) -> IncidentDetail:
        """Fresh snapshot including all evidence and the latest recorded decision."""
        ...

    def append_decision(self, data: DecisionCreate) -> str:
        """Append one row and its evidence links; return its generated public ID.

        Do not commit here. Do not persist a calculated deadline or edit history.
        """
        ...


class DecisionRepository(Protocol):
    def get_incident(self, incident_id: str) -> IncidentDetail | None:
        """Return a detached snapshot, current decision selected by recording order."""
        ...

    def transaction(self, incident_id: str) -> AbstractContextManager[DecisionTransaction]:
        """Lock then read; unknown incident raises 404. Commit once on success.

        Roll back every change on any exception, including commit failure.
        Serialize ordinary decisions for a single incident and coordinate reset.
        """
        ...


class DeadlineCalculator(Protocol):
    def calculate_deadline(self, determined_at: datetime) -> date:
        """Fourth business day AFTER the Eastern date, using the agreed holidays."""
        ...

    def describe_deadline(self, deadline: date | None, as_of: datetime) -> DeadlineStatus:
        """Eastern date boundary and business-day count; null means NOT_APPLICABLE.

        The implementation owns all counting conventions, including the integer
        businessDays value when no deadline applies. Inputs are aware instants.
        """
        ...


def utc_now() -> datetime:
    return datetime.now(UTC)


def decision_status(incident: IncidentDetail) -> IncidentStatus:
    """Derive state from the human decision; evidence never determines materiality."""
    if incident.status == IncidentStatus.FILED:
        # Preserve a future filing-aware repository's terminal state.
        return IncidentStatus.FILED
    if incident.current_decision is None:
        return IncidentStatus.OPEN
    if incident.current_decision.decision == MaterialityDecision.MATERIAL:
        return IncidentStatus.MATERIAL_PENDING_FILING
    return IncidentStatus.NOT_MATERIAL


class DecisionService:
    def __init__(
        self,
        repository: DecisionRepository,
        calendar: DeadlineCalculator,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self.repository = repository
        self.calendar = calendar
        self.clock = clock

    def get_incident(self, incident_id: str) -> IncidentDetail:
        incident = self.repository.get_incident(incident_id)
        if incident is None:
            raise ApiError(404, "NOT_FOUND", "Incident not found")
        return self._snapshot(incident)

    def _snapshot(self, incident: IncidentDetail) -> IncidentDetail:
        result = incident.model_copy(deep=True)
        result.status = decision_status(result)
        current = result.current_decision
        if current is not None:
            current.deadline = (
                self.calendar.calculate_deadline(current.determined_at)
                if current.decision == MaterialityDecision.MATERIAL
                else None
            )
        return result

    def record_decision(self, incident_id: str, data: DecisionCreate) -> DecisionCreated:
        # Validation runs on the locked snapshot, not the route's earlier read.
        with self.repository.transaction(incident_id) as transaction:
            incident = transaction.incident
            now = self.clock()
            if data.determined_at < incident.discovered_at or data.determined_at > now:
                raise ApiError(
                    400,
                    "INVALID_DETERMINED_AT",
                    "determinedAt must not be before discoveredAt or in the future",
                )
            owned = {item.evidence_id for item in incident.evidence}
            if any(item not in owned for item in data.evidence_ids):
                raise ApiError(
                    400, "INVALID_EVIDENCE_IDS", "evidenceIds must all belong to this incident"
                )
            if decision_status(incident) in (
                IncidentStatus.MATERIAL_PENDING_FILING,
                IncidentStatus.FILED,
            ):
                raise ApiError(409, "CONFLICT", "An ordinary decision is not allowed in this state")
            material = data.decision == MaterialityDecision.MATERIAL
            deadline = self.calendar.calculate_deadline(data.determined_at) if material else None
            decision_id = transaction.append_decision(data)
            result = DecisionCreated(
                decision_id=decision_id,
                status=(
                    IncidentStatus.MATERIAL_PENDING_FILING
                    if material
                    else IncidentStatus.NOT_MATERIAL
                ),
                deadline=deadline,
            )
        # The context has committed before success is returned to the caller.
        return result

    def deadline_status(self, incident_id: str, as_of: datetime | None = None) -> DeadlineStatus:
        incident = self.get_incident(incident_id)
        deadline = incident.current_decision.deadline if incident.current_decision else None
        return self.calendar.describe_deadline(
            deadline, as_of if as_of is not None else self.clock()
        )
