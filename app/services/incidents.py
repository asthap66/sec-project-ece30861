"""Incident/evidence operations; persistence is supplied by infrastructure."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from app.schemas import (
    EvidenceCreate,
    EvidenceResponse,
    IncidentCreate,
    IncidentDetail,
)


class IncidentNotFoundError(Exception):
    """The requested incident does not exist."""


class IncidentRepository(Protocol):
    """Adapter operations must complete atomically or roll back before raising.

    Implement using Person 1's database session/models. Enforce unique public IDs
    and the evidence foreign key in the database; never commit partial writes.
    Returned schema objects must be detached snapshots, not mutable stored state.
    """

    def create_incident(self, incident: IncidentDetail) -> None: ...

    def get_incident(self, incident_id: str) -> IncidentDetail | None: ...

    def add_evidence(self, incident_id: str, evidence: EvidenceResponse) -> None:
        """Atomically insert evidence; raise IncidentNotFoundError if parent is absent."""
        ...


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_public_id(prefix: str) -> str:
    """Provisional UUID format pending the shared public-ID decision."""
    return f"{prefix}-{uuid4().hex}"


class IncidentService:
    def __init__(
        self,
        repository: IncidentRepository,
        *,
        clock: Callable[[], datetime] = utc_now,
        id_factory: Callable[[str], str] = new_public_id,
    ) -> None:
        self.repository = repository
        self.clock = clock
        self.id_factory = id_factory

    def create_incident(self, data: IncidentCreate) -> IncidentDetail:
        incident = IncidentDetail(
            incident_id=self.id_factory("INC"),
            **data.model_dump(by_alias=False),
        )
        self.repository.create_incident(incident)
        return incident

    def get_incident(self, incident_id: str) -> IncidentDetail:
        incident = self.repository.get_incident(incident_id)
        if incident is None:
            raise IncidentNotFoundError(incident_id)
        return incident

    def attach_evidence(self, incident_id: str, data: EvidenceCreate) -> EvidenceResponse:
        self.get_incident(incident_id)
        evidence = EvidenceResponse(
            evidence_id=self.id_factory("EVD"),
            recorded_at=self.clock(),
            **data.model_dump(by_alias=False),
        )
        self.repository.add_evidence(incident_id, evidence)
        return evidence

    def get_evidence(self, incident_id: str) -> list[EvidenceResponse]:
        return self.get_incident(incident_id).evidence
