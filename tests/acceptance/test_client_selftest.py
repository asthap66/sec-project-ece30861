"""Self-tests for the acceptance client (no live service needed; runs in CI)."""

import httpx
import pytest

from tests.acceptance.client import API_KEY_HEADER, AcceptanceConfig, ApiClient, Auth

CONFIG = AcceptanceConfig(base_url="https://api.example.test", api_key="valid-key")


def _echo_client(config: AcceptanceConfig = CONFIG) -> tuple[ApiClient, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200)

    return ApiClient(config, transport=httpx.MockTransport(handler)), seen


def test_client_sends_configured_key() -> None:
    client, seen = _echo_client()
    client.get("/health")
    assert seen[0].headers[API_KEY_HEADER] == "valid-key"
    assert str(seen[0].url) == "https://api.example.test/health"


def test_client_omits_key_when_missing_even_if_caller_passes_one() -> None:
    client, seen = _echo_client()
    client.request("GET", "/x", auth=Auth.MISSING, headers={API_KEY_HEADER.lower(): "valid-key"})
    assert API_KEY_HEADER not in seen[0].headers


def test_client_wrong_key_differs_from_valid_key() -> None:
    for key in ("valid-key", "acceptance-test-wrong-key"):
        client, seen = _echo_client(AcceptanceConfig(base_url=CONFIG.base_url, api_key=key))
        client.get("/x", auth=Auth.WRONG)
        assert seen[0].headers[API_KEY_HEADER] != key


def test_client_refuses_valid_auth_without_api_key() -> None:
    client, _ = _echo_client(AcceptanceConfig(base_url=CONFIG.base_url, api_key=None))
    with pytest.raises(RuntimeError):
        client.get("/x")


def test_client_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BASE_URL", raising=False)
    assert AcceptanceConfig.from_env() is None

    monkeypatch.setenv("BASE_URL", "http://localhost:8000/")
    monkeypatch.setenv("API_KEY", "")
    config = AcceptanceConfig.from_env()
    assert config == AcceptanceConfig(base_url="http://localhost:8000", api_key=None)
    assert config.is_local and not config.is_https

    monkeypatch.setenv("BASE_URL", "ftp://example.test")
    with pytest.raises(ValueError):
        AcceptanceConfig.from_env()
