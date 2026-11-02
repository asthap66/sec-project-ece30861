"""Phase 4 domain routes. Course /test interfaces are unchanged."""

from json import JSONDecodeError
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app.routes.decision_support import get_decision_service
from app.schemas import DeadlineQuery, DeadlineStatus, DecisionCreate, DecisionCreated
from app.services.decisions import DecisionService

router = APIRouter(tags=["decisions"])
Service = Annotated[DecisionService, Depends(get_decision_service)]
IncidentId = Annotated[str, Path(alias="incidentId")]

decision_body_schema = DecisionCreate.model_json_schema(by_alias=True)
decision_definitions = decision_body_schema.pop("$defs", {})
decision_body_schema["properties"]["decision"] = decision_definitions["MaterialityDecision"]
ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    status: {"description": description}
    for status, description in (
        (400, "Invalid request; error and message identify the field"),
        (401, "Missing or invalid X-API-Key"),
        (404, "Unknown incident"),
        (503, "Persistence/calendar integration unavailable"),
    )
}


def request_errors(exc: ValidationError, location: str) -> RequestValidationError:
    return RequestValidationError(
        [{**error, "loc": (location, *error["loc"])} for error in exc.errors()]
    )


@router.post(
    "/incidents/{incidentId}/decisions",
    response_model=DecisionCreated,
    status_code=201,
    responses={**ERROR_RESPONSES, 409: {"description": "Ordinary decision conflicts with state"}},
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": decision_body_schema}},
        }
    },
)
async def record_decision(
    incident_id: IncidentId, request: Request, service: Service
) -> DecisionCreated:
    # Model 4: auth, route/method, parent, body, workflow state.
    await run_in_threadpool(service.get_incident, incident_id)
    try:
        body = await request.json()
    except (JSONDecodeError, UnicodeDecodeError) as exc:
        raise RequestValidationError(
            [{"type": "json_invalid", "loc": ("body",), "msg": "Invalid JSON"}]
        ) from exc
    try:
        data = DecisionCreate.model_validate(body)
    except ValidationError as exc:
        raise request_errors(exc, "body") from exc
    return await run_in_threadpool(service.record_decision, incident_id, data)


@router.get(
    "/incidents/{incidentId}/deadline-status",
    response_model=DeadlineStatus,
    responses=ERROR_RESPONSES,
    openapi_extra={
        "parameters": [
            {
                "name": "as_of",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "format": "date-time"},
                "description": "RFC 3339 timestamp with timezone; defaults to current time",
            }
        ]
    },
)
def deadline_status(incident_id: IncidentId, request: Request, service: Service) -> DeadlineStatus:
    service.get_incident(incident_id)
    try:
        query = DeadlineQuery.model_validate(dict(request.query_params))
    except ValidationError as exc:
        raise request_errors(exc, "query") from exc
    return service.deadline_status(incident_id, query.as_of)
