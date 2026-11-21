"""Black-box checks of the system endpoints and the shared error format.

Covers REQ-14 reset (AC-16, reset part), AC-03's GET half, and AC-14's error
bodies. Reset tests are destructive and only run with ALLOW_DESTRUCTIVE_TESTS=1.
"""

import pytest

from tests.acceptance.assertions import assert_error_body
from tests.acceptance.client import ApiClient, Auth
from tests.fixtures.data import unknown_incident_ids

pytestmark = pytest.mark.acceptance


def test_health_body_has_status(api: ApiClient) -> None:
    response = api.get("/health", auth=Auth.MISSING)
    assert response.status_code == 200
    assert isinstance(response.json().get("status"), str)


@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG], ids=["missing-key", "wrong-key"])
def test_401_uses_error_format(api: ApiClient, auth: Auth) -> None:
    assert_error_body(api.get("/incidents/INC-999999", auth=auth), 401)


@pytest.mark.parametrize("incident_id", unknown_incident_ids())
def test_unknown_incident_get_is_404_with_error_format(
    api: ApiClient, require_api_key: None, incident_id: str
) -> None:
    assert_error_body(api.get(f"/incidents/{incident_id}"), 404)


@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG], ids=["missing-key", "wrong-key"])
def test_reset_requires_key(api: ApiClient, allow_destructive: None, auth: Auth) -> None:
    # Destructive-gated: if auth were broken, this request would wipe the target.
    assert_error_body(api.post("/reset", auth=auth), 401)


def test_reset_succeeds_and_is_repeatable(api: ApiClient, reset_service: None) -> None:
    # reset_service has already reset once; a second reset on empty data must also work.
    response = api.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"status": "RESET_COMPLETE"}
