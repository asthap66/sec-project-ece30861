"""PostgreSQL-backed feature integration; only runs on TEST_DATABASE_URL.

Uses the existing disposable-database fixture and real production app provider.
No service/session overrides. The fixture migrates and resets the test database.
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app import db as db_module
from app.config import TITLE_MAX_LENGTH
from app.main import create_app
from app.models import Evidence, Incident
from tests.infrastructure.test_feature_routes import EVIDENCE, INCIDENT, KEY


def counts() -> tuple[int, int]:
    with db_module.get_session_factory()() as session:
        return (
            session.scalar(select(func.count()).select_from(Incident)) or 0,
            session.scalar(select(func.count()).select_from(Evidence)) or 0,
        )


def test_postgres_create_retrieve_evidence_restart_reset(database: str, client: TestClient) -> None:
    created = client.post("/incidents", json=INCIDENT, headers=KEY)
    assert created.status_code == 201
    assert created.json() == {"incidentId": "INC-001", "status": "OPEN"}
    other = client.post("/incidents", json=INCIDENT, headers=KEY)
    assert other.json()["incidentId"] == "INC-002"
    before = datetime.now(UTC)
    ids = []
    for category in ["TECHNICAL", "TECHNICAL", "TECHNICAL", "BUSINESS_IMPACT"]:
        response = client.post(
            "/incidents/INC-001/evidence", json={**EVIDENCE, "category": category}, headers=KEY
        )
        assert response.status_code == 201
        assert set(response.json()) == {"evidenceId", "recordedAt"}
        ids.append(response.json()["evidenceId"])
        recorded = datetime.fromisoformat(response.json()["recordedAt"])
        assert before <= recorded <= datetime.now(UTC)
    assert ids == ["EVD-001", "EVD-002", "EVD-003", "EVD-004"]
    assert counts() == (2, 4)
    detail = client.get("/incidents/INC-001", headers=KEY).json()
    assert set(detail) == {
        "incidentId",
        "title",
        "description",
        "discoveredAt",
        "reporterName",
        "status",
        "evidence",
        "currentDecision",
        "filing",
    }
    assert detail["discoveredAt"] == "2020-01-01T14:00:00Z"
    assert detail["currentDecision"] is detail["filing"] is None
    assert len(detail["evidence"]) == 4
    assert detail["evidence"][-1]["category"] == "BUSINESS_IMPACT"
    for item in detail["evidence"]:
        assert item["summary"] == EVIDENCE["summary"]
        assert item["source"] == EVIDENCE["source"]
        assert item["collectedAt"] == "2020-01-01T15:00:00Z"
        assert "incidentId" not in item
    assert client.get("/incidents/INC-002", headers=KEY).json()["evidence"] == []

    # New app instance and connection pool; not a real process/container restart.
    db_module.get_engine().dispose()
    db_module.get_session_factory.cache_clear()
    db_module.get_engine.cache_clear()
    with TestClient(create_app()) as restarted:
        assert restarted.get("/incidents/INC-001", headers=KEY).json() == detail
        assert restarted.post("/reset", headers=KEY).status_code == 200
        assert restarted.get("/incidents/INC-001", headers=KEY).status_code == 404
    assert counts() == (0, 0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("description", ""),
        ("discoveredAt", "2020-01-01T10:00:00"),
        ("discoveredAt", "9999-01-01T00:00:00Z"),
        ("title", "x" * (TITLE_MAX_LENGTH + 1)),
    ],
)
def test_postgres_invalid_incidents_do_not_write(
    database: str, client: TestClient, field: str, value: str
) -> None:
    response = client.post("/incidents", json={**INCIDENT, field: value}, headers=KEY)
    assert response.status_code == 400
    assert field in response.json()["message"]
    assert counts() == (0, 0)


def test_postgres_invalid_evidence_and_unknown_parent(database: str, client: TestClient) -> None:
    client.post("/incidents", json=INCIDENT, headers=KEY)
    for invalid in ({**EVIDENCE, "category": "INVALID"}, {"category": "TECHNICAL"}):
        response = client.post("/incidents/INC-001/evidence", json=invalid, headers=KEY)
        assert response.status_code == 400
        assert counts() == (1, 0)
    response = client.post("/incidents/INC-404/evidence", content="{", headers=KEY)
    assert response.status_code == 404
    assert counts() == (1, 0)
