"""AC-14 / REQ-13: X-API-Key authentication, checked before anything else."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import require_api_key
from tests.infrastructure.conftest import TEST_KEY

UNAUTHORIZED = {"error": "UNAUTHORIZED", "message": "missing or invalid API key"}


def test_health_needs_no_key(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


@pytest.mark.parametrize(
    "headers", [{}, {"X-API-Key": "wrong"}, {"X-API-Key": ""}], ids=["missing", "wrong", "empty"]
)
def test_bad_key_is_401_in_contract_format(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post("/reset", headers=headers)
    assert response.status_code == 401
    assert response.json() == UNAUTHORIZED


def test_header_name_is_case_insensitive(client: TestClient) -> None:
    """HTTP header names are case-insensitive, so x-api-key works too."""
    response = client.get("/incidents/INC-404", headers={"x-api-key": TEST_KEY})
    assert response.status_code != 401


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/incidents/INC-999"),  # unknown ID: 401, not 404
        ("DELETE", "/incidents/INC-001"),  # edit/delete attempt: 401, not 405
        ("POST", "/incidents"),  # (body would be invalid): 401, not 400
        ("GET", "/no/such/path"),
    ],
)
def test_key_is_checked_before_routing(client: TestClient, method: str, path: str) -> None:
    """docs/contract-issues.md #4: without a valid key nothing else is revealed."""
    response = client.request(method, path)
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_valid_key_reaches_the_app(client: TestClient) -> None:
    response = client.get("/incidents/INC-999", headers={"X-API-Key": TEST_KEY})
    assert response.status_code == 404


def test_blank_configured_key_rejects_everything(
    monkeypatch: pytest.MonkeyPatch, app: FastAPI
) -> None:
    """A server with API_KEY="" must not treat an empty header as valid."""
    from app.config import get_settings

    monkeypatch.setenv("API_KEY", "")
    get_settings.cache_clear()
    with TestClient(app) as client:
        assert client.post("/reset", headers={"X-API-Key": ""}).status_code == 401
    get_settings.cache_clear()


def test_require_api_key_dependency(settings_env: None) -> None:
    """The dependency form, for routes that want to state it explicitly."""
    from app.errors import register_error_handlers

    app = FastAPI()
    register_error_handlers(app)

    @app.get("/guarded", dependencies=[Depends(require_api_key)])
    def guarded() -> dict[str, str]:
        return {"ok": "yes"}

    with TestClient(app) as client:
        assert client.get("/guarded").status_code == 401
        assert client.get("/guarded").json() == UNAUTHORIZED
        assert client.get("/guarded", headers={"X-API-Key": TEST_KEY}).json() == {"ok": "yes"}


def test_responses_carry_request_id_and_commit(client: TestClient) -> None:
    """Q2: every response says which build served it; no secrets in headers."""
    response = client.get("/health")
    assert response.headers["x-request-id"]
    assert "x-app-commit" in response.headers
    assert TEST_KEY not in str(response.headers)
