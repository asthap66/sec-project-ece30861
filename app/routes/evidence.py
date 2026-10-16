"""Evidence attachment endpoint; persistence is delegated to the service."""

from json import JSONDecodeError
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app.routes.feature_support import get_incident_service
from app.schemas import EvidenceCreate, EvidenceCreated
from app.services.incidents import IncidentService

router = APIRouter()
Service = Annotated[IncidentService, Depends(get_incident_service)]

# Body parsing happens after parent lookup (Model 4), including malformed JSON.
# Keep the request model visible in OpenAPI despite the explicit parsing order.
evidence_body_schema = EvidenceCreate.model_json_schema(by_alias=True)
evidence_definitions = evidence_body_schema.pop("$defs", {})
evidence_body_schema["properties"]["category"] = evidence_definitions["EvidenceCategory"]


@router.post(
    "/incidents/{incidentId}/evidence",
    response_model=EvidenceCreated,
    status_code=201,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": evidence_body_schema}},
        }
    },
)
async def attach_evidence(
    incident_id: Annotated[str, Path(alias="incidentId")], request: Request, service: Service
) -> EvidenceCreated:
    await run_in_threadpool(service.get_incident, incident_id)
    try:
        body = await request.json()
    except (JSONDecodeError, UnicodeDecodeError) as exc:
        raise RequestValidationError(
            [{"type": "json_invalid", "loc": ("body",), "msg": "Invalid JSON"}]
        ) from exc
    try:
        data = EvidenceCreate.model_validate(body)
    except ValidationError as exc:
        errors = [{**error, "loc": ("body", *error["loc"])} for error in exc.errors()]
        raise RequestValidationError(errors) from exc
    evidence = await run_in_threadpool(service.attach_evidence, incident_id, data)
    return EvidenceCreated(evidence_id=evidence.evidence_id, recorded_at=evidence.recorded_at)
