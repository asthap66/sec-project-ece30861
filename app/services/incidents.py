"""Incident/evidence business operations and the shared SQLAlchemy adapter."""

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.errors import ApiError
from app.models import Evidence, Incident
from app.schemas import (
    EvidenceCreate,
    EvidenceResponse,
    IncidentCreate,
    IncidentDetail,
    IncidentStatus,
)


class IncidentNotFoundError(ApiError):
    def __init__(self, incident_id: str) -> None:
        super().__init__(404, "NOT_FOUND", "Incident not found")


class IncidentRepository(Protocol):
    """Writes commit atomically; results are detached API snapshots."""

    def create_incident(self, data: IncidentCreate) -> IncidentDetail: ...

    def get_incident(self, incident_id: str) -> IncidentDetail | None: ...

    def add_evidence(self, incident_id: str, data: EvidenceCreate) -> EvidenceResponse: ...


def evidence_snapshot(record: Evidence) -> EvidenceResponse:
    return EvidenceResponse(
        evidence_id=record.public_id,
        category=record.category,
        summary=record.summary,
        source=record.source,
        collected_at=record.collected_at,
        recorded_at=record.recorded_at,
    )


def incident_snapshot(record: Incident) -> IncidentDetail:
    return IncidentDetail(
        incident_id=record.public_id,
        title=record.title,
        description=record.description,
        discovered_at=record.discovered_at,
        reporter_name=record.reporter_name,
        status=IncidentStatus(record.status),
        evidence=[evidence_snapshot(item) for item in record.evidence],
    )


class SQLAlchemyIncidentRepository:
    """Uses Person 1's models, generated columns, and request-scoped session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_incident(self, data: IncidentCreate) -> IncidentDetail:
        record = Incident(**data.model_dump(by_alias=False), status="OPEN", evidence=[])
        try:
            self.session.add(record)
            self.session.flush()
            result = incident_snapshot(record)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise

    def get_incident(self, incident_id: str) -> IncidentDetail | None:
        record = self.session.scalar(
            select(Incident)
            .where(Incident.public_id == incident_id)
            .options(selectinload(Incident.evidence))
        )
        return incident_snapshot(record) if record is not None else None

    def add_evidence(self, incident_id: str, data: EvidenceCreate) -> EvidenceResponse:
        try:
            # Hold a parent lock until commit: concurrent test reset cannot delete
            # the parent between lookup and the evidence insert.
            parent = self.session.scalar(
                select(Incident).where(Incident.public_id == incident_id).with_for_update()
            )
            if parent is None:
                raise IncidentNotFoundError(incident_id)
            record = Evidence(incident_id=parent.id, **data.model_dump(by_alias=False))
            self.session.add(record)
            self.session.flush()
            result = evidence_snapshot(record)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise


class IncidentService:
    def __init__(self, repository: IncidentRepository) -> None:
        self.repository = repository

    def create_incident(self, data: IncidentCreate) -> IncidentDetail:
        return self.repository.create_incident(data)

    def get_incident(self, incident_id: str) -> IncidentDetail:
        incident = self.repository.get_incident(incident_id)
        if incident is None:
            raise IncidentNotFoundError(incident_id)
        return incident

    def attach_evidence(self, incident_id: str, data: EvidenceCreate) -> EvidenceResponse:
        return self.repository.add_evidence(incident_id, data)

    def get_evidence(self, incident_id: str) -> list[EvidenceResponse]:
        return self.get_incident(incident_id).evidence
