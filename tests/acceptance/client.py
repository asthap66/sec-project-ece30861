"""Reusable HTTP client for acceptance tests.

Owner: Mohit. The target service and key come from the environment
(BASE_URL, API_KEY), never from source code.
"""

import os
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlsplit

import httpx

API_KEY_HEADER = "X-API-Key"
LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "0.0.0.0"})  # noqa: S104


class Auth(Enum):
    """Which credential a request carries."""

    VALID = "valid"
    MISSING = "missing"
    WRONG = "wrong"


@dataclass(frozen=True)
class AcceptanceConfig:
    base_url: str
    api_key: str | None
    timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls) -> "AcceptanceConfig | None":
        """Return config from the environment, or None when BASE_URL is unset."""
        base_url = os.environ.get("BASE_URL", "").strip()
        if not base_url:
            return None
        scheme = urlsplit(base_url).scheme
        if scheme not in ("http", "https"):
            raise ValueError(f"BASE_URL must be an http(s) URL, got scheme {scheme!r}")
        api_key = os.environ.get("API_KEY", "").strip() or None
        return cls(base_url=base_url.rstrip("/"), api_key=api_key)

    @property
    def is_local(self) -> bool:
        return urlsplit(self.base_url).hostname in LOCAL_HOSTS

    @property
    def is_https(self) -> bool:
        return urlsplit(self.base_url).scheme == "https"


class ApiClient:
    """Thin wrapper over httpx that controls the API-key header per request."""

    def __init__(
        self, config: AcceptanceConfig, transport: httpx.BaseTransport | None = None
    ) -> None:
        self.config = config
        self._http = httpx.Client(
            base_url=config.base_url, timeout=config.timeout_seconds, transport=transport
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        auth: Auth = Auth.VALID,
        json: object = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        sent = {k: v for k, v in (headers or {}).items() if k.lower() != API_KEY_HEADER.lower()}
        if auth is Auth.VALID:
            if self.config.api_key is None:
                raise RuntimeError("API_KEY must be set for authenticated requests")
            sent[API_KEY_HEADER] = self.config.api_key
        elif auth is Auth.WRONG:
            sent[API_KEY_HEADER] = self.wrong_key()
        return self._http.request(method, path, json=json, params=params, headers=sent)

    def get(
        self, path: str, *, auth: Auth = Auth.VALID, params: dict[str, str] | None = None
    ) -> httpx.Response:
        return self.request("GET", path, auth=auth, params=params)

    def post(self, path: str, *, auth: Auth = Auth.VALID, json: object = None) -> httpx.Response:
        return self.request("POST", path, auth=auth, json=json)

    def wrong_key(self) -> str:
        """A key guaranteed to differ from the configured one."""
        candidate = "acceptance-test-wrong-key"
        return candidate if candidate != self.config.api_key else candidate + "-x"

    def close(self) -> None:
        self._http.close()
