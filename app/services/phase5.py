"""Phase 5 workflow; storage is supplied by the persistence owner."""

from contextlib import AbstractContextManager
from typing import Protocol

from app.errors import ApiError
from app.schemas import (
    CorrectionCreate,
    DeadlineState,
    DecisionCreated,
    FilingCreate,
    FilingCreated,
    FilingTimeliness,
    IncidentStatus,
    IncidentTimeline,
    MaterialityDecision,
)
from app.services.decisions import (
    DecisionRepository,
    DecisionService,
    DecisionTransaction,
    decision_status,
)


class Phase5Transaction(DecisionTransaction, Protocol):
    def append_correction(self, data: CorrectionCreate) -> str:
        """Append a replacement and persist its supersession link, without committing."""
        ...

    def append_filing(
        self, data: FilingCreate, timeliness: FilingTimeliness, business_days_late: int
    ) -> str:
        """Append a filing, without committing; the incident becomes FILED."""
        ...


class Phase5Repository(DecisionRepository, Protocol):
    def transaction(self, incident_id: str) -> AbstractContextManager[Phase5Transaction]:
        """Lock the incident and commit once, or roll back every change on failure."""
        ...

    def get_timeline(self, incident_id: str) -> IncidentTimeline:
        """Return a consistent, recording-ordered snapshot, or raise 404."""
        ...


class Phase5Service(DecisionService):
    repository: Phase5Repository

    def correct_decision(self, incident_id: str, data: CorrectionCreate) -> DecisionCreated:
        with self.repository.transaction(incident_id) as transaction:
            incident = transaction.incident
            if decision_status(incident) == IncidentStatus.FILED:
                raise ApiError(409, "CONFLICT", "A filed incident cannot be corrected")
            current = incident.current_decision
            if current is None or current.decision_id != data.corrects_decision_id:
                raise ApiError(
                    400,
                    "INVALID_CORRECTS_DECISION_ID",
                    "correctsDecisionId must identify the current decision",
                )
            self.validate_decision(incident, data)
            deadline = (
                self.calendar.calculate_deadline(data.determined_at)
                if data.decision == MaterialityDecision.MATERIAL
                else None
            )
            decision_id = transaction.append_correction(data)
            result = DecisionCreated(
                decision_id=decision_id,
                deadline=deadline,
                status=(
                    IncidentStatus.MATERIAL_PENDING_FILING
                    if deadline is not None
                    else IncidentStatus.NOT_MATERIAL
                ),
            )
        return result

    def record_filing(self, incident_id: str, data: FilingCreate) -> FilingCreated:
        with self.repository.transaction(incident_id) as transaction:
            incident = transaction.incident
            if (
                decision_status(incident) != IncidentStatus.MATERIAL_PENDING_FILING
                or incident.current_decision is None
            ):
                raise ApiError(
                    409, "CONFLICT", "Filing requires a material decision pending filing"
                )
            deadline = self.calendar.calculate_deadline(incident.current_decision.determined_at)
            description = self.calendar.describe_deadline(deadline, data.filed_at)
            late = description.status == DeadlineState.OVERDUE
            timeliness = FilingTimeliness.LATE if late else FilingTimeliness.ON_TIME
            days = description.business_days if late else 0
            filing_id = transaction.append_filing(data, timeliness, days)
            result = FilingCreated(
                filing_id=filing_id,
                status=IncidentStatus.FILED,
                timeliness=timeliness,
                business_days_late=days,
            )
        return result

    def timeline(self, incident_id: str) -> IncidentTimeline:
        return self.repository.get_timeline(incident_id)
