"""REQ-14 / AC-02 / AC-03: every error uses {"error": CODE, "message": ...}.

Validation failures are 400 (not FastAPI's 422) and name the bad field.
"""

from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.errors import ApiError
from tests.infrastructure.conftest import TEST_KEY

KEY = {"X-API-Key": TEST_KEY}


class SampleIncident(BaseModel):
    """Shaped like Astha's request schema: camelCase JSON names."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    title: str = Field(min_length=1)
    discovered_at: datetime


@pytest.fixture
def sample_client(app: FastAPI) -> TestClient:
    @app.post("/sample")
    def sample(body: SampleIncident) -> dict[str, str]:
        return {"title": body.title}

    @app.get("/sample/{sample_id}")
    def missing(sample_id: str) -> None:
        raise ApiError(404, "NOT_FOUND", f"sample {sample_id} not found")

    return TestClient(app)


def assert_error_format(body: object) -> None:
    assert isinstance(body, dict)
    assert set(body) == {"error", "message"}
    assert isinstance(body["error"], str) and body["error"]
    assert isinstance(body["message"], str) and body["message"]


def test_missing_field_is_400_naming_it(sample_client: TestClient) -> None:
    response = sample_client.post("/sample", json={"title": "x"}, headers=KEY)
    assert response.status_code == 400
    assert response.json() == {
        "error": "INVALID_DISCOVERED_AT",
        "message": "discoveredAt is required",
    }


def test_bad_value_is_400_naming_the_field(sample_client: TestClient) -> None:
    response = sample_client.post(
        "/sample", headers=KEY, json={"title": "", "discoveredAt": "2024-01-01T00:00:00Z"}
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "INVALID_TITLE"
    assert body["message"].startswith("title ")


def test_malformed_json_is_400(sample_client: TestClient) -> None:
    response = sample_client.post(
        "/sample", content=b"{not json", headers={**KEY, "Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_BODY"


def test_api_error_from_a_route(sample_client: TestClient) -> None:
    response = sample_client.get("/sample/abc", headers=KEY)
    assert response.status_code == 404
    assert response.json() == {"error": "NOT_FOUND", "message": "sample abc not found"}


def test_unknown_path_is_404_in_contract_format(client: TestClient) -> None:
    response = client.get("/incidents/INC-999", headers=KEY)
    assert response.status_code == 404
    assert_error_format(response.json())


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_edit_or_delete_is_405(client: TestClient, method: str) -> None:
    """REQ-07: stored data can't be edited or deleted through the API."""
    response = client.request(method, "/reset", headers=KEY)
    assert response.status_code == 405
    assert response.json()["error"] == "METHOD_NOT_ALLOWED"


def test_unexpected_errors_hide_internals(app: FastAPI) -> None:
    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("secret internal detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom", headers=KEY)
    assert response.status_code == 500
    assert response.json() == {"error": "INTERNAL_ERROR", "message": "an unexpected error occurred"}
    assert "secret" not in response.text
