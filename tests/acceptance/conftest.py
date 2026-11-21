"""Acceptance-test fixtures.

Owner: Mohit. Live-service tests carry the ``acceptance`` marker and skip
unless BASE_URL is set. Reset-based tests also need ALLOW_DESTRUCTIVE_TESTS=1
and must only target the agreed synthetic test service.
"""

import os
from collections.abc import Iterator

import pytest

from tests.acceptance.client import AcceptanceConfig, ApiClient


@pytest.fixture(scope="session")
def acceptance_config() -> AcceptanceConfig:
    config = AcceptanceConfig.from_env()
    if config is None:
        pytest.skip("BASE_URL not set; acceptance tests need a running service")
    return config


@pytest.fixture(scope="session")
def api(acceptance_config: AcceptanceConfig) -> Iterator[ApiClient]:
    client = ApiClient(acceptance_config)
    yield client
    client.close()


@pytest.fixture(scope="session")
def require_api_key(acceptance_config: AcceptanceConfig) -> None:
    if acceptance_config.api_key is None:
        pytest.skip("API_KEY not set; this test needs a valid key")


@pytest.fixture
def allow_destructive() -> None:
    """Skip unless the runner opted in to tests that can wipe the target's data."""
    if os.environ.get("ALLOW_DESTRUCTIVE_TESTS") != "1":
        pytest.skip("destructive test; set ALLOW_DESTRUCTIVE_TESTS=1 to run it")


@pytest.fixture
def reset_service(api: ApiClient, require_api_key: None, allow_destructive: None) -> None:
    """Clear the target's data. Destructive: opt-in only."""
    response = api.post("/reset")
    assert response.is_success, f"POST /reset failed: {response.status_code} {response.text}"
