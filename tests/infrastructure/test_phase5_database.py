"""Phase 5 corrections, filings and timeline on real PostgreSQL.

Owner: Srihari. Runs the real app with the production adapters against the
disposable TEST_DATABASE_URL database (skipped without it). Checks what HTTP
alone can't see: corrections append rows and never change the original, the
database itself refuses a second filing (also when two race), rejected
requests leave no rows, the timeline follows recording order, reset clears
the Phase 5 tables, data survives a restart, and migration 0004 upgrades a
populated Phase 4 database and downgrades cleanly.

Expected deadline and timeliness values are fixed calendar facts (the shared
Eastern calendar, deadline = 4th business day after the determination date),
written out here rather than computed with the production calendar.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app import db as db_module
from app.main import create_app
from app.models import Decision, Filing
from tests.infrastructure.test_decision_database import MATERIAL, decide, incident_with_evidence
from tests.infrastructure.test_feature_routes import KEY

pytestmark = pytest.mark.phase5

# MATERIAL is determined Mon 2025-09-29 (Eastern): deadline Fri 2025-10-03.
ON_TIME = {"filedAt": "2025-10-03T23:59:59-04:00", "accessionNumber": "0000000000-25-000001"}
LATE_MONDAY = {"filedAt": "2025-10-06T12:00:00-04:00", "accessionNumber": "0000000000-25-000002"}
CORRECTION = {
    **MATERIAL,
    "decision": "NOT_MATERIAL",
    "determinedAt": "2025-09-30T09:00:00-04:00",
    "rationale": "Impact re-assessed as immaterial.",
}


def counts() -> tuple[int, int]:
    with db_module.get_session_factory()() as session:
        return (
            session.scalar(select(func.count()).select_from(Decision)) or 0,
            session.scalar(select(func.count()).select_from(Filing)) or 0,
        )


def material(client: TestClient) -> tuple[str, str]:
    incident = incident_with_evidence(client)
    evidence = client.get(f"/incidents/{incident}", headers=KEY).json()["evidence"]
    made = decide(client, incident, evidenceIds=[evidence[0]["evidenceId"]])
    assert made.status_code == 201, made.text
    return incident, str(made.json()["decisionId"])


def correct(client: TestClient, incident: str, corrects: str, **changes: Any) -> Any:
    body = {**CORRECTION, "correctsDecisionId": corrects, **changes}
    return client.post(f"/incidents/{incident}/corrections", json=body, headers=KEY)


def file(client: TestClient, incident: str, body: dict[str, str] = ON_TIME) -> Any:
    return client.post(f"/incidents/{incident}/filing", json=body, headers=KEY)


def detail(client: TestClient, incident: str) -> Any:
    return client.get(f"/incidents/{incident}", headers=KEY).json()


def timeline(client: TestClient, incident: str) -> Any:
    return client.get(f"/incidents/{incident}/timeline", headers=KEY).json()


# ----------------------------------------------------------------- corrections


def test_correction_appends_and_keeps_the_original(database: str, client: TestClient) -> None:
    incident, original = material(client)
    made = correct(client, incident, original)
    assert made.status_code == 201, made.text
    assert made.json() == {"decisionId": "DEC-002", "status": "NOT_MATERIAL", "deadline": None}
    assert counts() == (2, 0)

    with db_module.get_session_factory()() as session:
        rows = {d.public_id: d for d in session.scalars(select(Decision))}
    assert rows["DEC-001"].decision == "MATERIAL"  # original unchanged
    assert rows["DEC-001"].corrects_decision_id is None
    assert rows["DEC-002"].corrects_decision_id == rows["DEC-001"].id

    now = detail(client, incident)
    assert now["status"] == "NOT_MATERIAL"
    assert now["currentDecision"]["decisionId"] == "DEC-002"


def test_correction_back_to_material_gets_its_own_deadline(
    database: str, client: TestClient
) -> None:
    incident, original = material(client)
    first = correct(client, incident, original)
    second = correct(
        client,
        incident,
        first.json()["decisionId"],
        decision="MATERIAL",
        determinedAt="2025-10-01T10:00:00-04:00",  # Wed -> Tue 2025-10-07
    )
    assert second.json() == {
        "decisionId": "DEC-003",
        "status": "MATERIAL_PENDING_FILING",
        "deadline": "2025-10-07",
    }
    assert counts() == (3, 0)


@pytest.mark.parametrize(
    "changes",
    [
        {"correctsDecisionId": "DEC-999"},
        {"evidenceIds": ["EVD-999"]},
        {"determinedAt": "2099-01-01T00:00:00Z"},
        {"rationale": "  "},
    ],
)
def test_rejected_correction_leaves_no_rows(
    database: str, client: TestClient, changes: dict[str, Any]
) -> None:
    incident, original = material(client)
    before, history = detail(client, incident), timeline(client, incident)
    assert correct(client, incident, original, **changes).status_code == 400
    assert counts() == (1, 0)
    assert detail(client, incident) == before and timeline(client, incident) == history


def test_a_superseded_decision_cannot_be_corrected_again(database: str, client: TestClient) -> None:
    incident, original = material(client)
    assert correct(client, incident, original).status_code == 201
    assert correct(client, incident, original).status_code == 400  # no longer current
    assert counts() == (2, 0)
    with db_module.get_engine().connect() as conn, pytest.raises(IntegrityError):
        # a second correction of DEC-001 straight into the table: the unique
        # link keeps the history a single chain
        conn.execute(
            text(
                "INSERT INTO decisions (incident_id, decision, determined_at, decided_by,"
                " rationale, corrects_decision_id) VALUES (1, 'MATERIAL', now(), 'x', 'y', 1)"
            )
        )


def test_correction_cannot_point_into_another_incident(database: str, client: TestClient) -> None:
    material(client)  # INC-001 / DEC-001
    material(client)  # INC-002 / DEC-002
    with db_module.get_engine().connect() as conn, pytest.raises(IntegrityError):
        conn.execute(
            text(
                "INSERT INTO decisions (incident_id, decision, determined_at, decided_by,"
                " rationale, corrects_decision_id) VALUES (2, 'MATERIAL', now(), 'x', 'y', 1)"
            )
        )


# --------------------------------------------------------------------- filings


@pytest.mark.parametrize(
    ("body", "timeliness", "late_days"),
    [(ON_TIME, "ON_TIME", 0), (LATE_MONDAY, "LATE", 1)],
)
def test_filing_is_stored_and_makes_the_incident_filed(
    database: str, client: TestClient, body: dict[str, str], timeliness: str, late_days: int
) -> None:
    incident, _ = material(client)
    made = file(client, incident, body)
    assert made.status_code == 201, made.text
    assert made.json() == {
        "filingId": "FIL-001",
        "status": "FILED",
        "timeliness": timeliness,
        "businessDaysLate": late_days,
    }
    now = detail(client, incident)
    assert now["status"] == "FILED"
    assert now["filing"]["filingId"] == "FIL-001"
    assert now["filing"]["accessionNumber"] == body["accessionNumber"]
    assert now["filing"]["timeliness"] == timeliness
    assert now["filing"]["businessDaysLate"] == late_days
    assert datetime.fromisoformat(now["filing"]["filedAt"]) == datetime.fromisoformat(
        body["filedAt"]
    )
    assert counts() == (1, 1)


def test_no_filing_without_a_pending_material_decision(database: str, client: TestClient) -> None:
    open_incident = incident_with_evidence(client)
    assert file(client, open_incident).status_code == 409
    not_material = incident_with_evidence(client)
    decide(client, not_material, decision="NOT_MATERIAL", evidenceIds=["EVD-002"])
    assert file(client, not_material).status_code == 409
    assert counts() == (1, 0)


def test_after_filing_nothing_else_is_accepted(database: str, client: TestClient) -> None:
    incident, original = material(client)
    assert file(client, incident).status_code == 201
    before, history = detail(client, incident), timeline(client, incident)
    assert file(client, incident, LATE_MONDAY).status_code == 409
    assert correct(client, incident, original).status_code == 409
    assert decide(client, incident).status_code == 409
    assert counts() == (1, 1)
    assert detail(client, incident) == before and timeline(client, incident) == history


def test_database_refuses_a_second_filing(database: str, client: TestClient) -> None:
    incident, _ = material(client)
    assert file(client, incident).status_code == 201
    with db_module.get_engine().connect() as conn, pytest.raises(IntegrityError):
        conn.execute(
            text(
                "INSERT INTO filings (incident_id, filed_at, accession_number, timeliness,"
                " business_days_late) VALUES (1, now(), 'dup', 'ON_TIME', 0)"
            )
        )


def test_concurrent_filings_serialize(database: str) -> None:
    app = create_app()
    with TestClient(app) as setup:
        incident, _ = material(setup)
    gate = Barrier(2)

    def submit(_: int) -> int:
        with TestClient(app) as client:
            gate.wait()
            return int(file(client, incident).status_code)

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = sorted(pool.map(submit, range(2)))
    assert codes == [201, 409]
    assert counts() == (1, 1)


# -------------------------------------------------------------------- timeline


def test_timeline_is_complete_and_in_recording_order(database: str, client: TestClient) -> None:
    incident, original = material(client)
    corrected = correct(
        client, incident, original, decision="MATERIAL", determinedAt="2025-09-30T09:00:00-04:00"
    ).json()["decisionId"]
    filed = file(client, incident).json()["filingId"]
    body = timeline(client, incident)
    assert [(e["eventType"], e["referenceId"]) for e in body["events"]] == [
        ("INCIDENT_CREATED", incident),
        ("EVIDENCE_ADDED", "EVD-001"),
        ("DECISION_RECORDED", original),
        ("DECISION_CORRECTED", corrected),
        ("FILING_RECORDED", filed),
    ]
    stamps = [datetime.fromisoformat(e["recordedAt"]) for e in body["events"]]
    assert stamps == sorted(stamps) and all(s.utcoffset() == timedelta(0) for s in stamps)
    assert body["evidenceCounts"] == {"technical": 0, "businessImpact": 1, "legal": 0, "other": 0}
    # discovered 2020-01-01T14:00Z (10:00-04:00), current decision 2025-09-30T13:00Z:
    # 1827 days to 2025-01-01 + 272 to 2025-09-30, less one hour = 2098.958
    assert body["discoveryToDeterminationDays"] == 2098.96


def test_timeline_orders_by_recording_not_by_entered_times(
    database: str, client: TestClient
) -> None:
    incident, original = material(client)  # determined 2025-09-29
    # the correction claims an EARLIER determination than the original; it was
    # still recorded later, so it comes later
    corrected = correct(
        client, incident, original, determinedAt="2025-01-02T09:00:00-05:00"
    ).json()["decisionId"]
    kinds = [e["referenceId"] for e in timeline(client, incident)["events"]][-2:]
    assert kinds == [original, corrected]


def test_timeline_of_a_new_incident(database: str, client: TestClient) -> None:
    incident = client.post(
        "/incidents",
        json={
            "title": "t",
            "description": "d",
            "discoveredAt": "2020-01-01T00:00:00Z",
            "reporterName": "r",
        },
        headers=KEY,
    ).json()["incidentId"]
    body = timeline(client, incident)
    assert [e["eventType"] for e in body["events"]] == ["INCIDENT_CREATED"]
    assert body["discoveryToDeterminationDays"] is None
    assert client.get("/incidents/INC-999/timeline", headers=KEY).status_code == 404


# ------------------------------------------------------- reset, restart, schema


def test_reset_and_restart_with_phase5_data(database: str, client: TestClient) -> None:
    incident, original = material(client)
    corrected = correct(client, incident, original, decision="MATERIAL").json()["decisionId"]
    assert file(client, incident).status_code == 201
    before, history = detail(client, incident), timeline(client, incident)
    assert before["currentDecision"]["decisionId"] == corrected

    # new app and connection pool: everything comes back from the database
    db_module.get_engine().dispose()
    db_module.get_session_factory.cache_clear()
    db_module.get_engine.cache_clear()
    with TestClient(create_app()) as restarted:
        assert detail(restarted, incident) == before
        assert timeline(restarted, incident) == history

        assert restarted.post("/reset", headers=KEY).status_code == 200
        assert counts() == (0, 0)
        assert restarted.get(f"/incidents/{incident}/timeline", headers=KEY).status_code == 404
        again, _ = material(restarted)
        assert file(restarted, again).json()["filingId"] == "FIL-001"  # numbering restarts


def test_test_setup_also_clears_phase5_data(database: str, client: TestClient) -> None:
    incident, _ = material(client)
    file(client, incident)
    setup = client.post(
        "/test/setup", json={"session_id": "phase5-reset-check", "setup": {}}, headers=KEY
    )
    assert setup.status_code == 201
    assert counts() == (0, 0)


def test_migration_upgrades_a_populated_phase4_database(database: str) -> None:
    from alembic import command
    from alembic.config import Config

    config = Config("alembic.ini")
    with TestClient(create_app()) as client:
        incident, original = material(client)
    command.downgrade(config, "0003")  # back to the Phase 4 schema, rows kept
    with db_module.get_engine().connect() as conn:
        assert conn.scalar(text("SELECT to_regclass('filings')")) is None
    command.upgrade(config, "head")
    with TestClient(create_app()) as client:
        current = detail(client, incident)
        assert current["status"] == "MATERIAL_PENDING_FILING"
        assert current["currentDecision"]["decisionId"] == original
        assert [e["eventType"] for e in timeline(client, incident)["events"]] == [
            "INCIDENT_CREATED",
            "EVIDENCE_ADDED",
            "DECISION_RECORDED",
        ]
        assert correct(client, incident, original).status_code == 201
        assert file(client, incident).status_code == 409  # now NOT_MATERIAL


def test_recording_times_use_the_insert_time(database: str) -> None:
    with db_module.get_engine().connect() as conn:
        defaults: dict[str, str] = dict(
            conn.execute(
                text(
                    "SELECT table_name || '.' || column_name, column_default"
                    " FROM information_schema.columns WHERE (table_name, column_name) IN"
                    " (('incidents','created_at'), ('evidence','recorded_at'),"
                    " ('decisions','recorded_at'), ('filings','recorded_at'))"
                )
            ).all()
        )
    assert len(defaults) == 4
    assert all("clock_timestamp()" in str(value) for value in defaults.values()), defaults


# ------------------------------------------------------------------ edge cases


def test_correcting_an_incident_with_no_decision_writes_nothing(
    database: str, client: TestClient
) -> None:
    incident = incident_with_evidence(client)
    assert correct(client, incident, "DEC-001").status_code == 400
    assert counts() == (0, 0)


def test_not_material_corrected_to_material_can_then_be_filed(
    database: str, client: TestClient
) -> None:
    incident = incident_with_evidence(client)
    first = decide(client, incident, decision="NOT_MATERIAL").json()["decisionId"]
    made = correct(client, incident, first, decision="MATERIAL")  # Tue 2025-09-30 -> Mon 10-06
    assert made.json()["deadline"] == "2025-10-06" and made.json()["status"] == (
        "MATERIAL_PENDING_FILING"
    )
    filed = file(client, incident, ON_TIME)  # Fri 10-03, before the corrected deadline
    assert filed.json()["timeliness"] == "ON_TIME"
    assert counts() == (2, 1)


def test_material_correction_outside_the_calendar_years_writes_nothing(
    database: str, client: TestClient
) -> None:
    incident, original = material(client)
    response = correct(
        client, incident, original, decision="MATERIAL", determinedAt="2024-06-03T12:00:00Z"
    )
    assert response.status_code == 400
    assert counts() == (1, 0)


def test_filing_outside_the_calendar_years_writes_nothing(
    database: str, client: TestClient
) -> None:
    incident, _ = material(client)
    late = {"filedAt": "2028-01-05T12:00:00-05:00", "accessionNumber": "x"}
    response = file(client, incident, late)
    assert response.status_code == 400 and response.json()["error"] == "DATE_OUT_OF_RANGE"
    assert counts() == (1, 0)
    assert detail(client, incident)["status"] == "MATERIAL_PENDING_FILING"


def test_late_on_a_weekend_is_late_with_zero_business_days(
    database: str, client: TestClient
) -> None:
    incident, _ = material(client)
    saturday = {"filedAt": "2025-10-04T00:00:00-04:00", "accessionNumber": "x"}  # deadline Fri
    made = file(client, incident, saturday).json()
    assert (made["timeliness"], made["businessDaysLate"]) == ("LATE", 0)
    assert detail(client, incident)["filing"]["businessDaysLate"] == 0


def test_concurrent_corrections_of_the_same_decision(database: str) -> None:
    app = create_app()
    with TestClient(app) as setup:
        incident, original = material(setup)
    gate = Barrier(2)

    def submit(_: int) -> int:
        with TestClient(app) as client:
            gate.wait()
            return int(correct(client, incident, original).status_code)

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = sorted(pool.map(submit, range(2)))
    assert codes == [201, 400]  # the loser's reference is no longer current
    assert counts() == (2, 0)


def test_correction_racing_a_filing_leaves_a_consistent_state(database: str) -> None:
    app = create_app()
    with TestClient(app) as setup:
        incident, original = material(setup)
    gate = Barrier(2)

    def run(which: str) -> tuple[str, int]:
        with TestClient(app) as client:
            gate.wait()
            response = (
                file(client, incident) if which == "file" else correct(client, incident, original)
            )
            return which, int(response.status_code)

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = dict(pool.map(run, ["file", "correct"]))
    with TestClient(app) as client:
        state = detail(client, incident)
    if codes["file"] == 201:  # filed first: a filed incident can't be corrected
        assert codes["correct"] == 409 and state["status"] == "FILED"
        assert counts() == (1, 1)
    else:  # corrected to NOT_MATERIAL first: nothing left to file
        assert codes == {"file": 409, "correct": 201} and state["status"] == "NOT_MATERIAL"
        assert counts() == (2, 0)


def test_evidence_after_filing_is_recorded_in_order(database: str, client: TestClient) -> None:
    incident, _ = material(client)
    filed = file(client, incident).json()["filingId"]
    for category in ("TECHNICAL", "LEGAL", "OTHER", "TECHNICAL"):
        response = client.post(
            f"/incidents/{incident}/evidence",
            json={
                "category": category,
                "summary": "s",
                "source": "x",
                "collectedAt": "2020-01-02T00:00:00Z",
            },
            headers=KEY,
        )
        assert response.status_code == 201
    body = timeline(client, incident)
    kinds = [e["eventType"] for e in body["events"]]
    assert kinds.index("FILING_RECORDED") == 3 and kinds[4:] == ["EVIDENCE_ADDED"] * 4
    assert body["events"][3]["referenceId"] == filed
    assert body["evidenceCounts"] == {"technical": 2, "businessImpact": 1, "legal": 1, "other": 1}


def test_ordinary_decision_after_a_not_material_correction(
    database: str, client: TestClient
) -> None:
    incident, original = material(client)
    corrected = correct(client, incident, original).json()["decisionId"]  # NOT_MATERIAL
    later = decide(client, incident, determinedAt="2025-10-01T10:00:00-04:00")
    assert later.status_code == 201
    events = [(e["eventType"], e["referenceId"]) for e in timeline(client, incident)["events"]]
    assert events[-3:] == [
        ("DECISION_RECORDED", original),
        ("DECISION_CORRECTED", corrected),
        ("DECISION_RECORDED", later.json()["decisionId"]),
    ]
    assert detail(client, incident)["currentDecision"]["decisionId"] == later.json()["decisionId"]


def test_downgrade_with_phase5_rows_then_upgrade(database: str) -> None:
    from alembic import command
    from alembic.config import Config

    config = Config("alembic.ini")
    with TestClient(create_app()) as client:
        incident, original = material(client)
        correct(client, incident, original, decision="MATERIAL")
        assert file(client, incident).status_code == 201
    command.downgrade(config, "0003")  # filings dropped; both decisions kept
    with db_module.get_engine().connect() as conn:
        assert conn.scalar(text("SELECT count(*) FROM decisions")) == 2
    command.upgrade(config, "head")
    with TestClient(create_app()) as client:
        assert detail(client, incident)["status"] == "MATERIAL_PENDING_FILING"
        assert file(client, incident).status_code == 201
