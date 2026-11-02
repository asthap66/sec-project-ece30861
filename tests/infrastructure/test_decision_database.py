"""Phase 4 decisions on real PostgreSQL (REQ-04/05/07/08/09/10/14/15).

Owner: Srihari. Runs the real app with the production adapters (no fakes or
dependency overrides) against the disposable TEST_DATABASE_URL database.
Checks what HTTP alone can't see: rejected requests leave no decision or link
rows, concurrent decisions serialize, the database refuses foreign evidence,
reset clears decisions, and the migration upgrades a Phase 3 database.
"""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app import db as db_module
from app.main import create_app
from app.models import Decision, DecisionEvidence
from tests.infrastructure.test_feature_routes import EVIDENCE, INCIDENT, KEY

# INCIDENT is discovered 2020-01-01, so 2025 determinations are after discovery.
MATERIAL = {
    "decision": "MATERIAL",
    "determinedAt": "2025-09-29T12:00:00-04:00",
    "decidedBy": "Disclosure Committee",
    "rationale": "Operational and financial impact is material.",
    "evidenceIds": ["EVD-001"],
}


def rows() -> tuple[int, int]:
    with db_module.get_session_factory()() as session:
        return (
            session.scalar(select(func.count()).select_from(Decision)) or 0,
            session.scalar(select(func.count()).select_from(DecisionEvidence)) or 0,
        )


def incident_with_evidence(client: TestClient, evidence: int = 1) -> str:
    incident = client.post("/incidents", json=INCIDENT, headers=KEY).json()["incidentId"]
    for _ in range(evidence):
        response = client.post(f"/incidents/{incident}/evidence", json=EVIDENCE, headers=KEY)
        assert response.status_code == 201
    return str(incident)


def decide(client: TestClient, incident: str, **changes: Any) -> Any:
    return client.post(
        f"/incidents/{incident}/decisions", json={**MATERIAL, **changes}, headers=KEY
    )


def test_material_decision_round_trip(database: str, client: TestClient) -> None:
    incident = incident_with_evidence(client, evidence=2)
    made = decide(client, incident, evidenceIds=["EVD-002", "EVD-001", "EVD-002"])
    assert made.status_code == 201
    assert made.json() == {
        "decisionId": "DEC-001",
        "status": "MATERIAL_PENDING_FILING",
        "deadline": "2025-10-03",
    }
    assert rows() == (1, 3)

    detail = client.get(f"/incidents/{incident}", headers=KEY).json()
    assert detail["status"] == "MATERIAL_PENDING_FILING"
    assert detail["currentDecision"] == {
        "decisionId": "DEC-001",
        "decision": "MATERIAL",
        "determinedAt": "2025-09-29T16:00:00Z",
        "decidedBy": MATERIAL["decidedBy"],
        "rationale": MATERIAL["rationale"],
        "evidenceIds": ["EVD-002", "EVD-001", "EVD-002"],  # order and repeats kept
        "deadline": "2025-10-03",
    }
    status = client.get(
        f"/incidents/{incident}/deadline-status",
        params={"as_of": "2025-10-06T12:00:00Z"},
        headers=KEY,
    )
    assert status.json() == {"status": "OVERDUE", "deadline": "2025-10-03", "businessDays": 1}


@pytest.mark.parametrize(
    "changes",
    [
        {"determinedAt": "2019-12-31T23:59:59Z"},  # before discovery
        {"determinedAt": "2099-01-01T00:00:00Z"},  # future
        {"evidenceIds": ["EVD-999"]},  # unknown
        {"evidenceIds": ["EVD-001", "EVD-002"]},  # EVD-002 belongs to another incident
        {"evidenceIds": []},
        {"decision": "PROBABLY_MATERIAL"},
        {"rationale": "   "},
        {"determinedAt": "2024-06-03T12:00:00Z"},  # outside the calendar's years
    ],
)
def test_rejected_decisions_leave_no_rows(
    database: str, client: TestClient, changes: dict[str, Any]
) -> None:
    incident = incident_with_evidence(client)
    incident_with_evidence(client)  # owns EVD-002
    before = client.get(f"/incidents/{incident}", headers=KEY).json()
    response = decide(client, incident, **changes)
    assert response.status_code == 400
    assert rows() == (0, 0)
    assert client.get(f"/incidents/{incident}", headers=KEY).json() == before


def test_second_decision_while_pending_is_409_and_changes_nothing(
    database: str, client: TestClient
) -> None:
    incident = incident_with_evidence(client)
    assert decide(client, incident).status_code == 201
    before = client.get(f"/incidents/{incident}", headers=KEY).json()
    for decision in ("MATERIAL", "NOT_MATERIAL"):
        assert decide(client, incident, decision=decision).status_code == 409
    assert rows() == (1, 1)
    assert client.get(f"/incidents/{incident}", headers=KEY).json() == before


def test_not_material_then_material(database: str, client: TestClient) -> None:
    incident = incident_with_evidence(client)
    first = decide(client, incident, decision="NOT_MATERIAL")
    assert first.json() == {"decisionId": "DEC-001", "status": "NOT_MATERIAL", "deadline": None}
    na = client.get(
        f"/incidents/{incident}/deadline-status",
        params={"as_of": "2025-10-01T12:00:00Z"},
        headers=KEY,
    ).json()
    assert na == {"status": "NOT_APPLICABLE", "deadline": None, "businessDays": 0}

    second = decide(client, incident, determinedAt="2025-10-10T12:00:00-04:00")
    assert second.json()["decisionId"] == "DEC-002"
    assert second.json()["deadline"] == "2025-10-17"
    current = client.get(f"/incidents/{incident}", headers=KEY).json()["currentDecision"]
    assert current["decisionId"] == "DEC-002"  # newest recorded, both rows kept
    assert rows() == (2, 2)


def test_concurrent_material_decisions_serialize(database: str) -> None:
    app = create_app()
    with TestClient(app) as setup:
        incident = incident_with_evidence(setup)
    gate = Barrier(2)

    def submit(_: int) -> int:
        with TestClient(app) as client:
            gate.wait()
            return int(decide(client, incident).status_code)

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = sorted(pool.map(submit, range(2)))
    assert codes == [201, 409]
    assert rows() == (1, 1)


def test_database_refuses_evidence_from_another_incident(database: str, client: TestClient) -> None:
    incident_with_evidence(client)  # INC-001 / EVD-001
    incident_with_evidence(client)  # INC-002 / EVD-002
    assert decide(client, "INC-001").status_code == 201
    with db_module.get_engine().connect() as conn, pytest.raises(IntegrityError):
        # link DEC-001 (incident 1) to EVD-002 (incident 2), bypassing the service
        conn.execute(
            text(
                "INSERT INTO decision_evidence (decision_id, position, incident_id, evidence_id)"
                " VALUES (1, 5, 1, 2)"
            )
        )


def test_reset_and_restart(database: str, client: TestClient) -> None:
    incident = incident_with_evidence(client)
    decide(client, incident)
    detail = client.get(f"/incidents/{incident}", headers=KEY).json()

    # new app and connection pool (not a container restart; see W055 for that)
    db_module.get_engine().dispose()
    db_module.get_session_factory.cache_clear()
    db_module.get_engine.cache_clear()
    with TestClient(create_app()) as restarted:
        assert restarted.get(f"/incidents/{incident}", headers=KEY).json() == detail
        assert restarted.post("/reset", headers=KEY).status_code == 200
        assert restarted.get(f"/incidents/{incident}", headers=KEY).status_code == 404
        assert rows() == (0, 0)
        # numbering restarts after reset
        again = incident_with_evidence(restarted)
        assert decide(restarted, again).json()["decisionId"] == "DEC-001"


def test_migration_upgrades_a_phase3_database(database: str) -> None:
    from alembic import command
    from alembic.config import Config

    config = Config("alembic.ini")
    command.downgrade(config, "0002")
    with db_module.get_engine().begin() as conn:
        conn.execute(
            text(
                "INSERT INTO incidents (title, description, discovered_at, reporter_name)"
                " VALUES ('Phase 3', 'Existing row', '2020-01-01T00:00:00Z', 'SOC')"
            )
        )
    command.upgrade(config, "head")
    with TestClient(create_app()) as client:
        detail = client.get("/incidents/INC-001", headers=KEY).json()
        assert (detail["title"], detail["status"], detail["currentDecision"]) == (
            "Phase 3",
            "OPEN",
            None,
        )
        client.post("/incidents/INC-001/evidence", json=EVIDENCE, headers=KEY)
        assert decide(client, "INC-001").status_code == 201
