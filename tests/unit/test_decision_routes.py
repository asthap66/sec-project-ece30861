"""Real FastAPI middleware/routes with test-only Phase 4 dependencies."""

from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.main import create_app
from app.routes.decision_support import (
    get_deadline_calculator,
    get_decision_repository,
    get_optional_decision_service,
)
from app.routes.feature_support import get_incident_service
from app.schemas import DeadlineState, DeadlineStatus, EvidenceCreate, IncidentCreate
from app.services.decisions import DecisionService
from app.services.incidents import IncidentService
from tests.unit.decision_fakes import StubCalendar, TestDecisionRepository
from tests.unit.test_decisions import NOW, PAYLOAD

KEY = {"X-API-Key": "phase4-unit-key"}


@pytest.fixture
def route_workflow(
    monkeypatch: pytest.MonkeyPatch,
    incident_payload: dict[str, str],
    evidence_payload: dict[str, str],
) -> Iterator[tuple[TestClient, TestDecisionRepository, StubCalendar]]:
    monkeypatch.setenv("API_KEY", KEY["X-API-Key"])
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://unused:unused@127.0.0.1:1/unused")
    get_settings.cache_clear()
    repository = TestDecisionRepository()
    repository.create_incident(IncidentCreate.model_validate(incident_payload))
    repository.add_evidence("INC-001", EvidenceCreate.model_validate(evidence_payload))
    calendar = StubCalendar()
    app = create_app()
    # Exercise the production optional-service wiring and existing GET provider.
    app.dependency_overrides[get_decision_repository] = lambda: repository
    app.dependency_overrides[get_deadline_calculator] = lambda: calendar
    app.dependency_overrides[get_db] = lambda: Mock(spec=Session)
    with TestClient(app) as client:
        yield client, repository, calendar
    get_settings.cache_clear()


def test_http_decision_and_existing_retrieval(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar],
) -> None:
    client, _, _ = route_workflow
    made = client.post("/incidents/INC-001/decisions", json=PAYLOAD, headers=KEY)
    assert made.status_code == 201
    assert set(made.json()) == {"decisionId", "status", "deadline"}
    detail = client.get("/incidents/INC-001", headers=KEY).json()
    assert detail["currentDecision"]["decisionId"] == made.json()["decisionId"]
    assert detail["status"] == "MATERIAL_PENDING_FILING"
    assert len(detail["evidence"]) == 1 and detail["filing"] is None
    assert made.headers["x-request-id"] and "x-app-commit" in made.headers


@pytest.mark.parametrize("body", ["{", "null", "[]", "{}", '"bad"'])
def test_parent_lookup_precedes_body_validation(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar], body: str
) -> None:
    client, repository, _ = route_workflow
    assert client.post("/incidents/missing/decisions", content=body, headers=KEY).status_code == 404
    response = client.post("/incidents/INC-001/decisions", content=body, headers=KEY)
    assert response.status_code == 400 and set(response.json()) == {"error", "message"}
    assert repository.history == []


def test_exact_enum_error_and_409(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar],
) -> None:
    client, repository, _ = route_workflow
    response = client.post(
        "/incidents/INC-001/decisions",
        json={**PAYLOAD, "decision": "PROBABLY_MATERIAL"},
        headers=KEY,
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": "INVALID_DECISION",
        "message": "decision must be MATERIAL or NOT_MATERIAL",
    }
    assert client.post("/incidents/INC-001/decisions", json=PAYLOAD, headers=KEY).status_code == 201
    assert client.post("/incidents/INC-001/decisions", json=PAYLOAD, headers=KEY).status_code == 409
    assert len(repository.history) == 1


@pytest.mark.parametrize("path", ["decisions", "deadline-status"])
@pytest.mark.parametrize("key", [None, "wrong"])
def test_authentication_first(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar],
    path: str,
    key: str | None,
) -> None:
    client, _, _ = route_workflow
    headers = {} if key is None else {"X-API-Key": key}
    response = client.request(
        "POST" if path == "decisions" else "GET",
        f"/incidents/missing/{path}",
        headers=headers,
        content="{",
    )
    assert response.status_code == 401 and set(response.json()) == {"error", "message"}


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
@pytest.mark.parametrize("path", ["decisions", "deadline-status"])
def test_append_only_methods(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar], method: str, path: str
) -> None:
    client, repository, _ = route_workflow
    response = client.request(method, f"/incidents/INC-001/{path}", headers=KEY)
    assert response.status_code == 405 and repository.history == []


@pytest.mark.parametrize("as_of", ["bad", "2025-10-01T12:00:00", "123", ""])
def test_as_of_validation_and_lookup_order(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar], as_of: str
) -> None:
    client, _, _ = route_workflow
    params = {"as_of": as_of}
    response = client.get("/incidents/INC-001/deadline-status", params=params, headers=KEY)
    assert response.status_code == 400 and "as_of" in response.json()["message"]
    assert (
        client.get("/incidents/missing/deadline-status", params=params, headers=KEY).status_code
        == 404
    )


@pytest.mark.parametrize("status", [DeadlineState.PENDING, DeadlineState.OVERDUE])
def test_status_uses_calendar_result(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar], status: DeadlineState
) -> None:
    client, _, calendar = route_workflow
    assert client.post("/incidents/INC-001/decisions", json=PAYLOAD, headers=KEY).status_code == 201
    calendar.result = DeadlineStatus(
        status=status, deadline=calendar.result.deadline, business_days=2
    )
    response = client.get(
        "/incidents/INC-001/deadline-status", params={"as_of": "2025-10-06T12:00:00Z"}, headers=KEY
    )
    assert response.status_code == 200
    assert response.json() == calendar.result.model_dump(mode="json")
    assert calendar.described[-1][1] == datetime(2025, 10, 6, 12, tzinfo=UTC)


def test_evidence_does_not_decide_and_remains_appendable(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar],
    evidence_payload: dict[str, str],
) -> None:
    client, repository, calendar = route_workflow
    app = client.app
    assert hasattr(app, "dependency_overrides")
    service = DecisionService(repository, calendar, lambda: NOW)
    app.dependency_overrides[get_incident_service] = lambda: IncidentService(repository, service)
    response = client.get("/incidents/INC-001/deadline-status", headers=KEY)
    assert response.json() == {"status": "NOT_APPLICABLE", "deadline": None, "businessDays": 0}
    assert client.get("/incidents/INC-001", headers=KEY).json()["status"] == "OPEN"
    client.post("/incidents/INC-001/decisions", json=PAYLOAD, headers=KEY)
    before = client.get("/incidents/INC-001", headers=KEY).json()
    evidence_payload["summary"] = "Severe synthetic impact"
    response = client.post("/incidents/INC-001/evidence", json=evidence_payload, headers=KEY)
    assert response.status_code == 201
    after = client.get("/incidents/INC-001", headers=KEY).json()
    assert len(after["evidence"]) == 2
    assert after["currentDecision"] == before["currentDecision"] and len(repository.history) == 1


def test_unconnected_dependencies_are_explicit(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar],
) -> None:
    client, _, _ = route_workflow
    app = client.app
    assert hasattr(app, "dependency_overrides")
    app.dependency_overrides[get_optional_decision_service] = lambda: None
    for method, path in (("POST", "decisions"), ("GET", "deadline-status")):
        response = client.request(method, f"/incidents/INC-001/{path}", headers=KEY)
        assert response.status_code == 503
        assert response.json()["error"] == "PHASE4_DEPENDENCIES_UNAVAILABLE"


def test_openapi_exposes_domain_schema(
    route_workflow: tuple[TestClient, TestDecisionRepository, StubCalendar],
) -> None:
    client, _, _ = route_workflow
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/incidents/{incidentId}/decisions"]["post"]
    body = operation["requestBody"]["content"]["application/json"]["schema"]
    assert set(body["required"]) == set(PAYLOAD)
    assert body["properties"]["decision"]["enum"] == ["MATERIAL", "NOT_MATERIAL"]
    assert "409" in operation["responses"] and "400" in operation["responses"]
    parameters = schema["paths"]["/incidents/{incidentId}/deadline-status"]["get"]["parameters"]
    assert any(item["name"] == "as_of" and not item["required"] for item in parameters)
