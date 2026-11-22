"""PostgreSQL adapter for Astha's Phase5Repository protocol (corrections,
filings, timeline). Owner: Srihari.

Builds on the Phase 4 adapter (decision_store.py) and keeps its rules:
the request's own Session, one write path through transaction(), which locks
the incident row (SELECT ... FOR UPDATE), lets the service validate the fresh
snapshot, and commits once or rolls back everything.

- append_correction inserts a NEW decision row with corrects_decision_id
  pointing at the one it replaces. Nothing is updated or deleted, so the
  original stays in the history (REQ-07). The newest row is the current
  decision, as in Phase 4.
- append_filing inserts the filing. filings.incident_id is unique, so a
  second filing fails in the database even if the service check were skipped.
- get_timeline reads under a shared lock on the incident (FOR SHARE): it waits
  for a write in progress to commit and blocks new writes while it reads, so
  the events, counts and duration come from one consistent state.

Timeline order is recording order: recorded_at (set by the database with
clock_timestamp(), migration 0004), then the event kind, then the row id for
ties. User-entered times (determinedAt, collectedAt, filedAt) are never used
for ordering.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import ApiError
from app.models import Decision, DecisionEvidence, Evidence, Filing, Incident
from app.schemas import (
    CorrectionCreate,
    EvidenceCounts,
    FilingCreate,
    FilingTimeliness,
    HistoryEvent,
    HistoryEventType,
    IncidentTimeline,
)
from app.services.decision_store import SQLAlchemyDecisionRepository, _Transaction
from app.services.incidents import IncidentNotFoundError

# tie-break for events stamped at the same instant: the order they can happen in
_KIND_ORDER = {
    HistoryEventType.INCIDENT_CREATED: 0,
    HistoryEventType.EVIDENCE_ADDED: 1,
    HistoryEventType.DECISION_RECORDED: 2,
    HistoryEventType.DECISION_CORRECTED: 2,
    HistoryEventType.FILING_RECORDED: 3,
}
_COUNT_FIELDS = {
    "TECHNICAL": "technical",
    "BUSINESS_IMPACT": "business_impact",
    "LEGAL": "legal",
    "OTHER": "other",
}
SECONDS_PER_DAY = 86_400


def discovery_to_determination_days(discovered_at: datetime, determined_at: datetime) -> float:
    """Elapsed days from discovery to the current decision's determination:
    exact instants (timezone-independent), rounded to 2 decimal places.
    Provisional pod rule; see docs/phase5/srihari-persistence-handoff.md."""
    return round((determined_at - discovered_at).total_seconds() / SECONDS_PER_DAY, 2)


class _Phase5Transaction(_Transaction):
    def _insert_decision(self, data: CorrectionCreate, corrects: int | None) -> str:
        evidence_ids = {item.public_id: item for item in self.record.evidence}
        if any(ref not in evidence_ids for ref in data.evidence_ids):
            raise ApiError(
                400, "INVALID_EVIDENCE_IDS", "evidenceIds must all belong to this incident"
            )
        decision = Decision(
            incident_id=self.record.id,
            decision=data.decision.value,
            determined_at=data.determined_at,
            decided_by=data.decided_by,
            rationale=data.rationale,
            corrects_decision_id=corrects,
        )
        self.session.add(decision)
        self.session.flush()
        self.session.add_all(
            DecisionEvidence(
                decision_id=decision.id,
                position=position,
                incident_id=self.record.id,
                evidence_id=evidence_ids[ref].id,
            )
            for position, ref in enumerate(data.evidence_ids)
        )
        self.session.flush()
        return decision.public_id

    def append_correction(self, data: CorrectionCreate) -> str:
        # the service already checked this is the current decision, on this
        # same locked snapshot; resolve it to its row inside the lock
        predecessor = self.session.scalar(
            select(Decision.id).where(
                Decision.incident_id == self.record.id,
                Decision.public_id == data.corrects_decision_id,
            )
        )
        if predecessor is None:
            raise ApiError(
                400,
                "INVALID_CORRECTS_DECISION_ID",
                "correctsDecisionId must identify the current decision",
            )
        return self._insert_decision(data, corrects=predecessor)

    def append_filing(
        self, data: FilingCreate, timeliness: FilingTimeliness, business_days_late: int
    ) -> str:
        filing = Filing(
            incident_id=self.record.id,
            filed_at=data.filed_at,
            accession_number=data.accession_number,
            timeliness=timeliness.value,
            business_days_late=business_days_late,
        )
        self.session.add(filing)
        self.session.flush()
        return filing.public_id


class SQLAlchemyPhase5Repository(SQLAlchemyDecisionRepository):
    """Phase 4 decisions plus Phase 5 corrections, filings and timeline."""

    @contextmanager
    def transaction(self, incident_id: str) -> Iterator[_Phase5Transaction]:
        try:
            self.session.rollback()  # lock and snapshot from one fresh transaction
            record = self._incident(incident_id, lock=True)
            if record is None:
                raise IncidentNotFoundError(incident_id)
            yield _Phase5Transaction(self.session, record)
            self.session.commit()
        except BaseException:
            self.session.rollback()
            raise

    def get_timeline(self, incident_id: str) -> IncidentTimeline:
        try:
            self.session.rollback()
            incident = self.session.scalar(
                select(Incident)
                .where(Incident.public_id == incident_id)
                .with_for_update(read=True, of=Incident)
            )
            if incident is None:
                raise IncidentNotFoundError(incident_id)
            return self._timeline(incident)
        finally:
            self.session.rollback()  # release the shared lock; nothing was written

    def _timeline(self, incident: Incident) -> IncidentTimeline:
        rows: list[tuple[datetime, int, int, HistoryEventType, str]] = []

        def add(kind: HistoryEventType, at: datetime, row_id: int, public_id: str) -> None:
            rows.append((at, _KIND_ORDER[kind], row_id, kind, public_id))

        add(HistoryEventType.INCIDENT_CREATED, incident.created_at, incident.id, incident.public_id)
        counts = dict.fromkeys(_COUNT_FIELDS.values(), 0)
        for evidence in self.session.scalars(
            select(Evidence).where(Evidence.incident_id == incident.id)
        ):
            add(
                HistoryEventType.EVIDENCE_ADDED,
                evidence.recorded_at,
                evidence.id,
                evidence.public_id,
            )
            counts[_COUNT_FIELDS[evidence.category]] += 1
        decisions = list(
            self.session.scalars(
                select(Decision).where(Decision.incident_id == incident.id).order_by(Decision.id)
            )
        )
        for decision in decisions:
            kind = (
                HistoryEventType.DECISION_CORRECTED
                if decision.corrects_decision_id is not None
                else HistoryEventType.DECISION_RECORDED
            )
            add(kind, decision.recorded_at, decision.id, decision.public_id)
        filing = self.session.scalar(select(Filing).where(Filing.incident_id == incident.id))
        if filing is not None:
            add(HistoryEventType.FILING_RECORDED, filing.recorded_at, filing.id, filing.public_id)

        rows.sort(key=lambda row: row[:3])
        current = decisions[-1] if decisions else None
        return IncidentTimeline(
            incident_id=incident.public_id,
            events=[
                HistoryEvent(event_type=kind, recorded_at=at, reference_id=public_id)
                for at, _, _, kind, public_id in rows
            ],
            evidence_counts=EvidenceCounts(**counts),
            discovery_to_determination_days=(
                discovery_to_determination_days(incident.discovered_at, current.determined_at)
                if current is not None
                else None
            ),
        )


def count_filings(session: Session) -> int:
    """Rows in filings (used by the reset and persistence checks)."""
    return session.scalar(select(func.count()).select_from(Filing)) or 0
