"""PostgreSQL adapter for Astha's DecisionRepository protocol (REQ-04, REQ-08).

Owner: Srihari. Uses the request's own Session from get_db(); it never makes
a second engine or session.

transaction() is the only write path:
1. SELECT ... FOR UPDATE on the incident row. Two decisions for the same
   incident queue here, so the second one validates against the first one's
   committed result and gets 409 (REQ-08). Reset's TRUNCATE also waits for
   the lock, so it can't remove the incident mid-decision.
2. The caller validates and calls append_decision(), which inserts and
   flushes but never commits.
3. One commit when the with-block ends normally; any exception, including a
   failed commit, rolls back every row, so a rejected decision leaves nothing
   behind (REQ-05).
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.errors import ApiError
from app.models import Decision, DecisionEvidence, Evidence, Incident
from app.schemas import DecisionCreate, DecisionDetail, IncidentDetail
from app.services.decisions import DecisionTransaction
from app.services.incidents import IncidentNotFoundError, incident_snapshot


def _load(session: Session, incident: Incident) -> IncidentDetail:
    """Incident, all its evidence and its newest decision, as a detached snapshot."""
    snapshot = incident_snapshot(incident)
    current = session.scalar(
        select(Decision)
        .where(Decision.incident_id == incident.id)
        .order_by(Decision.id.desc())
        .limit(1)
        .options(selectinload(Decision.evidence_links))
    )
    if current is not None:
        linked = [link.evidence_id for link in current.evidence_links]
        public_ids = {
            row.id: row.public_id
            for row in session.execute(
                select(Evidence.id, Evidence.public_id).where(Evidence.id.in_(linked))
            )
        }
        snapshot.current_decision = DecisionDetail(
            decision_id=current.public_id,
            decision=current.decision,
            determined_at=current.determined_at,
            decided_by=current.decided_by,
            rationale=current.rationale,
            evidence_ids=[public_ids[link.evidence_id] for link in current.evidence_links],
            deadline=None,  # DecisionService computes it from the shared calendar
        )
    return snapshot


class _Transaction:
    def __init__(self, session: Session, incident: Incident) -> None:
        self.session = session
        self.record = incident
        self.incident = _load(session, incident)

    def append_decision(self, data: DecisionCreate) -> str:
        evidence_ids = {item.public_id: item for item in self.record.evidence}
        missing = [ref for ref in data.evidence_ids if ref not in evidence_ids]
        if missing:  # the service checks this first; this guards direct callers
            raise ApiError(
                400, "INVALID_EVIDENCE_IDS", "evidenceIds must all belong to this incident"
            )
        decision = Decision(
            incident_id=self.record.id,
            decision=data.decision.value,
            determined_at=data.determined_at,
            decided_by=data.decided_by,
            rationale=data.rationale,
        )
        self.session.add(decision)
        self.session.flush()  # generates decision.id and public_id
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


class SQLAlchemyDecisionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _incident(self, incident_id: str, lock: bool) -> Incident | None:
        query = (
            select(Incident)
            .where(Incident.public_id == incident_id)
            .options(selectinload(Incident.evidence))
        )
        if lock:
            query = query.with_for_update(of=Incident)
        return self.session.scalar(query)

    def get_incident(self, incident_id: str) -> IncidentDetail | None:
        record = self._incident(incident_id, lock=False)
        return _load(self.session, record) if record is not None else None

    @contextmanager
    def transaction(self, incident_id: str) -> Iterator[DecisionTransaction]:
        try:
            # end any read-only transaction the request already opened, so the
            # lock and the snapshot come from one fresh transaction
            self.session.rollback()
            record = self._incident(incident_id, lock=True)
            if record is None:
                raise IncidentNotFoundError(incident_id)
            yield _Transaction(self.session, record)
            self.session.commit()
        except BaseException:
            self.session.rollback()
            raise
