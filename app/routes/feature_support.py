"""Feature-local error mapping until shared infrastructure is integrated."""

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic.alias_generators import to_camel

from app.services.incidents import IncidentNotFoundError, IncidentService


class FeatureRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def handle(request: Request) -> Response:
            try:
                return await handler(request)
            except RequestValidationError as exc:
                fields = sorted(
                    {
                        to_camel(str(error["loc"][1]))
                        for error in exc.errors()
                        if len(error["loc"]) > 1 and isinstance(error["loc"][1], str)
                    }
                )
                message = (
                    f"Invalid request fields: {', '.join(fields)}"
                    if fields
                    else "Invalid request body"
                )
                return JSONResponse(
                    status_code=400,
                    content={"error": "INVALID_REQUEST", "message": message},
                )
            except IncidentNotFoundError:
                return JSONResponse(
                    status_code=404,
                    content={"error": "NOT_FOUND", "message": "Incident not found"},
                )

        return handle


def get_incident_service() -> IncidentService:
    """Person 1 must supply a request-scoped persistent repository adapter."""
    raise HTTPException(status_code=503, detail="Incident persistence is not configured")
