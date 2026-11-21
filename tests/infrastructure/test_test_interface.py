"""Course testing interface, system side: POST /test/setup and GET /test/report.

Spec: "Cross-team Testing Interface", section "System" and "Execution rules".
Database tests need TEST_DATABASE_URL (they reset it).
"""

import json
import os
import subprocess
import sys
import textwrap

import pytest
from fastapi.testclient import TestClient

from tests.infrastructure.conftest import TEST_KEY

KEY = {"X-API-Key": TEST_KEY}
INCIDENT = {
    "title": "Order system ransomware",
    "description": "Encryption detected.",
    "discoveredAt": "2026-09-21T14:30:00-04:00",
    "reporterName": "SOC",
}


def setup(client: TestClient, session_id: str, **extra: object) -> object:
    return client.post(
        "/test/setup", json={"session_id": session_id, "setup": {}, **extra}, headers=KEY
    )


def assert_interface_error(response: object, status: int) -> None:
    assert response.status_code == status  # type: ignore[attr-defined]
    body = response.json()  # type: ignore[attr-defined]
    assert body["source"] == "system"
    assert isinstance(body["message"], str) and body["message"]


def test_setup_returns_the_same_id(database: str, client: TestClient) -> None:
    response = setup(client, "run-123")
    assert response.status_code == 201  # type: ignore[attr-defined]
    assert response.json() == {"session_id": "run-123"}  # type: ignore[attr-defined]


def test_setup_resets_to_an_empty_baseline(database: str, client: TestClient) -> None:
    client.post("/incidents", json=INCIDENT, headers=KEY)
    setup(client, "run-a")
    assert client.get("/incidents/INC-001", headers=KEY).status_code == 404
    created = client.post("/incidents", json=INCIDENT, headers=KEY).json()
    assert created["incidentId"] == "INC-001"  # IDs restart for each session


def test_session_id_can_be_used_once(database: str, client: TestClient) -> None:
    assert setup(client, "run-once").status_code == 201  # type: ignore[attr-defined]
    assert_interface_error(setup(client, "run-once"), 409)


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"session_id": ""},
        {"session_id": "   "},
        {"session_id": 5},
        {"session_id": "x", "setup": "not an object"},
        {"session_id": "x" * 201},
    ],
    ids=["empty", "blank-id", "whitespace-id", "number-id", "bad-setup", "too-long"],
)
def test_invalid_setup_is_400(database: str, client: TestClient, body: dict[str, object]) -> None:
    assert_interface_error(client.post("/test/setup", json=body, headers=KEY), 400)


def test_setup_body_that_is_not_json_is_400(database: str, client: TestClient) -> None:
    response = client.post(
        "/test/setup", content=b"nope", headers={**KEY, "Content-Type": "application/json"}
    )
    assert_interface_error(response, 400)


def test_setup_without_setup_field_is_accepted(database: str, client: TestClient) -> None:
    response = client.post("/test/setup", json={"session_id": "run-no-setup"}, headers=KEY)
    assert response.status_code == 201


def test_test_endpoints_need_the_key_and_say_where_errors_come_from(client: TestClient) -> None:
    for response in (
        client.post("/test/setup", json={"session_id": "x"}),
        client.get("/test/report?session_id=x"),
    ):
        assert_interface_error(response, 401)


def test_report_for_unknown_session_is_404(database: str, client: TestClient) -> None:
    assert_interface_error(client.get("/test/report?session_id=nope", headers=KEY), 404)


def test_report_without_session_id_is_400(database: str, client: TestClient) -> None:
    assert_interface_error(client.get("/test/report", headers=KEY), 400)


def test_report_has_the_spec_shape(database: str, client: TestClient) -> None:
    setup(client, "run-report")
    client.post("/incidents", json=INCIDENT, headers=KEY)
    response = client.get("/test/report?session_id=run-report", headers=KEY)
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "run-report"
    code = body["coverage"]["code"]
    assert set(code) == {"covered", "total", "basis"}
    assert code["basis"]
    # coverage is off in tests (APP_COVERAGE unset): null counts, never a made-up 0
    assert code["covered"] is None and code["total"] is None
    assert "disabled" in code["basis"]


def test_reading_the_report_runs_no_project_operations(database: str, client: TestClient) -> None:
    setup(client, "run-readonly")
    client.post("/incidents", json=INCIDENT, headers=KEY)
    client.get("/test/report?session_id=run-readonly", headers=KEY)
    assert client.get("/incidents/INC-001", headers=KEY).status_code == 200
    assert client.get("/incidents/INC-002", headers=KEY).status_code == 404


def test_real_coverage_counts_lines_per_session() -> None:
    """With APP_COVERAGE=1, each session counts only the lines run after its setup.

    Run in a separate process so starting coverage can't disturb this test run.
    """
    script = textwrap.dedent("""
        import json
        from app.coverage_runtime import SessionCoverage
        from app import errors

        cov = SessionCoverage()
        cov.start()
        with cov.interface_request():          # like POST /test/setup
            cov.begin_session("s1")
        errors.validation_error([{"loc": ("body", "title"), "msg": "x", "type": "missing"}])
        with cov.interface_request():          # like GET /test/report
            first = cov.measure("s1")
        with cov.interface_request():          # reading again changes nothing
            again = cov.measure("s1")
        with cov.interface_request():
            cov.begin_session("s2")
        with cov.interface_request():
            s2 = cov.measure("s2")
        print(json.dumps([first, again, s2]))
    """)
    env = {**os.environ, "APP_COVERAGE": "1"}
    out = subprocess.run(  # noqa: S603 - runs our own fixed script
        [sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True
    )
    s1, again, s2 = json.loads(out.stdout.strip().splitlines()[-1])
    assert isinstance(s1["covered"], int) and isinstance(s1["total"], int)
    assert 0 < s1["covered"] <= s1["total"]
    assert again == s1  # the spec: reading the report does not change it
    assert s2["covered"] == 0 and s2["total"] == s1["total"]  # nothing ran in s2 yet
    assert s1["basis"]
