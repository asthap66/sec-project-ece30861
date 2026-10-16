"""AC-14: public health, API-key enforcement, and HTTPS deployment.

Assumption (docs/contract-issues.md #4): authentication is checked before the
resource lookup, so an unknown incident ID without a valid key returns 401.
Error body format is not asserted until the contract defines it.
"""

import pytest

from tests.acceptance.client import ApiClient, Auth

pytestmark = pytest.mark.acceptance

# Synthetic ID that no service should contain; used only to reach an authenticated route.
UNKNOWN_INCIDENT_PATH = "/incidents/acceptance-unknown-id-000"


def test_health_is_public(api: ApiClient) -> None:
    response = api.get("/health", auth=Auth.MISSING)
    assert response.status_code == 200


@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG], ids=["missing-key", "wrong-key"])
def test_authenticated_route_rejects_bad_key(api: ApiClient, auth: Auth) -> None:
    response = api.get(UNKNOWN_INCIDENT_PATH, auth=auth)
    assert response.status_code == 401


def test_authenticated_route_accepts_valid_key(api: ApiClient, require_api_key: None) -> None:
    response = api.get(UNKNOWN_INCIDENT_PATH)
    assert response.status_code != 401


def test_deployment_uses_https(api: ApiClient) -> None:
    if api.config.is_local:
        pytest.skip("local target; HTTPS is only required for the deployment")
    assert api.config.is_https, f"deployed BASE_URL must use https: {api.config.base_url}"
