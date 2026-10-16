"""Adapter transaction failures using mocked sessions, not PostgreSQL."""

from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.schemas import EvidenceCreate, IncidentCreate
from app.services.incidents import IncidentNotFoundError, SQLAlchemyIncidentRepository


def test_create_rolls_back_failed_insert(incident_payload: dict[str, str]) -> None:
    session = Mock(spec=Session)
    session.flush.side_effect = RuntimeError("synthetic insert failure")
    repository = SQLAlchemyIncidentRepository(session)
    with pytest.raises(RuntimeError, match="synthetic insert failure"):
        repository.create_incident(IncidentCreate.model_validate(incident_payload))
    session.rollback.assert_called_once()
    session.commit.assert_not_called()


def test_attach_missing_parent_never_inserts(evidence_payload: dict[str, str]) -> None:
    session = Mock(spec=Session)
    session.scalar.return_value = None
    repository = SQLAlchemyIncidentRepository(session)
    with pytest.raises(IncidentNotFoundError):
        repository.add_evidence("INC-404", EvidenceCreate.model_validate(evidence_payload))
    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_called_once()
