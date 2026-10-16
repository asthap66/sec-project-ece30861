"""Scaffold smoke test: NOT acceptance coverage.

Confirms the application package imports and FastAPI can generate an OpenAPI
document. It says nothing about contract conformance or business behavior.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_app_imports_and_generates_openapi() -> None:
    schema = app.openapi()

    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == app.title


def test_openapi_endpoint_is_served() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["version"] == app.version
