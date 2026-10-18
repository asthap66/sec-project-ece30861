"""FastAPI application entry point.

Owner: Srihari (infrastructure).

Registers the middleware, error handlers and routers. Feature routers
(incidents, evidence) are added here as they are implemented against the
agreed contract.
"""

import logging
import os
import re
import time
import uuid
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.auth import API_KEY_HEADER, ApiKeyMiddleware
from app.errors import register_error_handlers
from app.routes import system

logger = logging.getLogger("app.requests")

# The git commit this build came from, set at image build time (Dockerfile
# GIT_COMMIT build arg). Sent on every response as X-App-Commit so anyone can
# check which version is deployed (submission Q2, commit mapping).
APP_COMMIT = os.environ.get("GIT_COMMIT", "unknown")

# IDs that appear in paths (INC-001, EVD-001, ...), logged so a request can be
# traced to the record it touched without logging any of the record's content.
_PUBLIC_ID = re.compile(r"\b(?:INC|EVD|DEC|FIL)-\d+\b")


class RequestLogMiddleware:
    """One log line per request: id, method, path, status, duration, record IDs.

    Never logs headers (they carry the API key) or request/response bodies
    (they carry incident details).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = uuid.uuid4().hex[:12]
        started = time.perf_counter()
        status = 500

        async def send_with_status(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                headers.append((b"x-app-commit", APP_COMMIT.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        finally:
            ids = ",".join(_PUBLIC_ID.findall(scope["path"])) or "-"
            logger.info(
                "request_id=%s method=%s path=%s status=%s duration_ms=%.1f ids=%s",
                request_id,
                scope["method"],
                scope["path"],
                status,
                (time.perf_counter() - started) * 1000,
                ids,
            )


def _document_api_key(application: FastAPI) -> None:
    """Declare the X-API-Key header in the OpenAPI document.

    Documentation only: it gives the /docs page an "Authorize" button, so the
    key can be entered once and every "Try it out" request sends it. The
    actual check is ApiKeyMiddleware, which runs whether or not this exists.
    /health is marked as needing no key, as in the contract.
    """

    def openapi() -> dict[str, Any]:
        if application.openapi_schema is None:
            schema = get_openapi(
                title=application.title,
                version=application.version,
                routes=application.routes,
            )
            schema.setdefault("components", {})["securitySchemes"] = {
                "ApiKey": {"type": "apiKey", "in": "header", "name": API_KEY_HEADER}
            }
            schema["security"] = [{"ApiKey": []}]
            for method in schema.get("paths", {}).get("/health", {}).values():
                method["security"] = []
            application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = openapi  # type: ignore[method-assign]


def create_app() -> FastAPI:
    application = FastAPI(
        title="Cybersecurity Incident and Evidence Management API",
        version="0.1.0",
    )
    register_error_handlers(application)
    application.include_router(system.router)
    # Middleware runs outermost-last-added: logging wraps auth, so rejected
    # requests (401) are logged too.
    application.add_middleware(ApiKeyMiddleware)
    application.add_middleware(RequestLogMiddleware)
    _document_api_key(application)
    return application


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
app = create_app()
