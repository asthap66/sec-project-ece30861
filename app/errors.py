"""Shared error helpers and exception handlers.

Owner: Srihari (infrastructure).

Every error the API returns has the pod contract's format (Phase 2 - Pod.pdf,
Q5.2): {"error": "ERROR_CODE", "message": "Description of the error"}.

For routes (Astha's code): raise ApiError instead of returning error bodies by
hand, so every team member's errors look the same:

    raise ApiError(404, "NOT_FOUND", f"incident {incident_id} not found")

Validation failures become 400 (not FastAPI's default 422). The code names the
first bad field, the way the contract's only example does
(INVALID_DECISION for the decision field): a bad discoveredAt gives
INVALID_DISCOVERED_AT, and the message starts with the field name (AC-02).
"""

import logging
import re
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")

# Codes for the non-validation errors. The contract fixes the format and status
# codes but not these names; they are listed in docs/contract-issues.md #4 for
# the pod to confirm.
STATUS_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    500: "INTERNAL_ERROR",
}


class ApiError(Exception):
    """Raise from a route to return a contract-format error."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def error_response(
    status_code: int, code: str, message: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    """The one place error bodies are built."""
    return JSONResponse(
        status_code=status_code, content={"error": code, "message": message}, headers=headers
    )


def _upper_snake(name: str) -> str:
    """discoveredAt -> DISCOVERED_AT"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def _field_name(location: Sequence[Any]) -> str | None:
    """The field a validation error is about, from pydantic's error location.

    ("body", "discoveredAt") -> "discoveredAt"; ("body", "evidenceIds", 0) ->
    "evidenceIds"; ("body",) -> None (the body as a whole was bad).
    """
    parts = [str(p) for p in location if not isinstance(p, int)]
    if parts and parts[0] in ("body", "query", "path", "header"):
        parts = parts[1:]
    return parts[0] if parts else None


def validation_error(errors: Sequence[Any]) -> JSONResponse:
    """400 naming the first bad field."""
    first = errors[0] if errors else {}
    field = _field_name(first.get("loc", ()))
    # pydantic prefixes messages from custom validators ("Value error, ...");
    # that's an internal detail, so drop it
    reason = re.sub(
        r"^(Value error|Assertion failed), ", "", str(first.get("msg", "invalid value"))
    )
    if first.get("type") == "json_invalid":
        return error_response(400, "INVALID_BODY", "request body must be valid JSON")
    if field is None:
        return error_response(400, "INVALID_BODY", f"request body is invalid: {reason}")
    code = f"INVALID_{_upper_snake(field)}"
    if first.get("type") == "missing":
        return error_response(400, code, f"{field} is required")
    return error_response(400, code, f"{field}: {reason}")


async def _handle_api_error(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, ApiError):  # registered for this type only
        raise exc
    return _with_source(request, error_response(exc.status_code, exc.code, exc.message))


async def _handle_validation(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):  # registered for this type only
        raise exc
    return _with_source(request, validation_error(exc.errors()))


async def _handle_http(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI/Starlette's own errors (unknown path, wrong method, ...)."""
    if not isinstance(exc, StarletteHTTPException):  # registered for this type only
        raise exc
    code = STATUS_CODES.get(exc.status_code, "HTTP_ERROR")
    if exc.status_code == 404:
        message = "resource not found"
    elif exc.status_code == 405:
        # REQ-07: stored records can't be edited or deleted through the API
        message = f"{request.method} is not allowed on {request.url.path}"
    else:
        message = str(exc.detail)
    return _with_source(
        request,
        error_response(exc.status_code, code, message, headers=getattr(exc, "headers", None)),
    )


async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    # Log the details server-side; never send internals (or data) to the client.
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return _with_source(
        request, error_response(500, "INTERNAL_ERROR", "an unexpected error occurred")
    )


def _with_source(request: Request, response: JSONResponse) -> JSONResponse:
    """Testing-interface paths (/test/...) need a "source" field on errors."""
    if request.url.path.startswith("/test/"):
        import json

        body = json.loads(bytes(response.body))
        body["source"] = "system"
        return JSONResponse(
            status_code=response.status_code,
            content=body,
            headers={
                k: v
                for k, v in response.headers.items()
                if k.lower() not in ("content-length", "content-type")
            },
        )
    return response


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, _handle_api_error)
    app.add_exception_handler(RequestValidationError, _handle_validation)
    app.add_exception_handler(StarletteHTTPException, _handle_http)
    app.add_exception_handler(Exception, _handle_unexpected)
