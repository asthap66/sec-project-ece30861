"""FastAPI application entry point.

Owner: Srihari (infrastructure).

Registers the middleware, error handlers and routers. Feature routers
(incidents, evidence) are added here as they are implemented against the
agreed contract.
"""

import logging
import re
import time
import uuid

from fastapi import FastAPI
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.auth import ApiKeyMiddleware
from app.errors import register_error_handlers
from app.routes import system

logger = logging.getLogger("app.requests")

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
    return application


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
app = create_app()
