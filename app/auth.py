"""X-API-Key authentication (REQ-13, AC-14).

Owner: Srihari (infrastructure).

Every endpoint except GET /health needs a valid key in the X-API-Key header;
a missing or wrong key gets 401 in the contract's error format.

The check runs as middleware, before routing. That way the key is checked
first for every request, including ones for IDs or methods that don't exist:
without a key you get 401, never a 404/405/400 that reveals something about
the data. This is the precedence the acceptance tests assume
(docs/contract-issues.md #4).

require_api_key() is the same check as a FastAPI dependency, for routes that
want to state it explicitly; with the middleware in place it is a second line
of defence, not a requirement.
"""

import hmac
import logging

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import get_settings
from app.errors import ApiError, error_response

API_KEY_HEADER = "X-API-Key"

# Paths that don't need a key: the health check (contract), plus FastAPI's
# generated docs, which describe the API but expose no data.
PUBLIC_PATHS = frozenset({"/health", "/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"})

logger = logging.getLogger("app.auth")


def key_is_valid(provided: str | None) -> bool:
    """Constant-time comparison against the configured key."""
    if not provided:
        return False
    expected = get_settings().api_key.get_secret_value()
    if not expected:
        return False  # a blank configured key must never mean "no auth"
    return hmac.compare_digest(provided.encode(), expected.encode())


def require_api_key(request: Request) -> None:
    """FastAPI dependency: 401 unless X-API-Key matches."""
    if not key_is_valid(request.headers.get(API_KEY_HEADER)):
        raise ApiError(401, "UNAUTHORIZED", "missing or invalid API key")


class ApiKeyMiddleware:
    """Rejects requests without a valid key before they reach any route."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return
        headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope["headers"]}
        try:
            allowed = key_is_valid(headers.get(API_KEY_HEADER.lower()))
        except Exception:  # noqa: BLE001 - e.g. API_KEY not configured: fail closed
            logger.error("API key check failed; is API_KEY configured?")
            response = error_response(500, "INTERNAL_ERROR", "server is not configured")
            await response(scope, receive, send)
            return
        if not allowed:
            response = error_response(401, "UNAUTHORIZED", "missing or invalid API key")
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
