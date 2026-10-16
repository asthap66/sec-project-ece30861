"""REQ-14 / REQ-15 / AC-16 (infrastructure side): reset, IDs and persistence.

Needs TEST_DATABASE_URL (a disposable PostgreSQL); skipped otherwise. Mohit's
acceptance tests check the same things against the deployed service.
"""

from datetime import UTC, datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app import db as db_module
from app.models import Evidence, Incident
from tests.infrastructure.conftest import TEST_KEY

KEY = {"X-API-Key": TEST_KEY}


def _add_incident(title: str = "Order system ransomware") -> Incident:
    with db_module.get_session_factory()() as session:
        incident = Incident(
            title=title,
            description="Encryption detected.",
            reporter_name="SOC",
            discovered_at=datetime(2026, 9, 21, 14, 30, tzinfo=timezone(timedelta(hours=-4))),
        )
        session.add(incident)
        session.flush()
        session.add(
            Evidence(
                incident_id=incident.id,
                category="TECHNICAL",
                summary="EDR alert",
                source="EDR",
                collected_at=datetime(2026, 9, 21, 15, tzinfo=UTC),
            )
        )
        session.commit()
        return incident


def test_ids_have_the_contract_format(database: str) -> None:
    first, second = _add_incident(), _add_incident("Second")
    assert (first.public_id, second.public_id) == ("INC-001", "INC-002")
    with db_module.get_session_factory()() as session:
        evidence = session.scalars(select(Evidence)).all()
    assert [e.public_id for e in evidence] == ["EVD-001", "EVD-002"]


def test_timestamps_keep_the_instant_and_are_timezone_aware(database: str) -> None:
    _add_incident()
    with db_module.get_session_factory()() as session:
        incident = session.scalars(select(Incident)).one()
    assert incident.discovered_at.tzinfo is not None
    # 14:30 at -04:00 is 18:30 UTC (the contract's own example)
    assert incident.discovered_at.astimezone(UTC) == datetime(2026, 9, 21, 18, 30, tzinfo=UTC)
    assert incident.created_at.tzinfo is not None
    assert incident.status == "OPEN"


def test_data_survives_a_new_connection_pool(database: str) -> None:
    """Close every connection (like an app restart) and read the data back."""
    _add_incident()
    db_module.get_engine().dispose()
    db_module.get_session_factory.cache_clear()
    db_module.get_engine.cache_clear()
    with db_module.get_session_factory()() as session:
        assert session.scalars(select(Incident.public_id)).all() == ["INC-001"]


def test_reset_clears_everything_and_restarts_ids(database: str, client: TestClient) -> None:
    _add_incident()
    _add_incident()
    response = client.post("/reset", headers=KEY)
    assert response.status_code == 200
    assert response.json() == {"status": "RESET_COMPLETE"}
    with db_module.get_session_factory()() as session:
        assert session.scalars(select(Incident)).all() == []
        assert session.scalars(select(Evidence)).all() == []
    assert _add_incident().public_id == "INC-001"


def test_evidence_cannot_outlive_its_incident(database: str) -> None:
    """The foreign key blocks deleting an incident that still has evidence."""
    import pytest
    from sqlalchemy import delete
    from sqlalchemy.exc import IntegrityError

    _add_incident()
    with db_module.get_session_factory()() as session, pytest.raises(IntegrityError):
        session.execute(delete(Incident))
        session.commit()
