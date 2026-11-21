"""Contract routes; unavailable until the Phase 5 repository is integrated."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path

from app.deadline_calendar import SHARED_CALENDAR
from app.errors import ApiError
from app.schemas import (
    CorrectionCreate,
    DecisionCreated,
    FilingCreate,
    FilingCreated,
    IncidentTimeline,
)
from app.services.phase5 import Phase5Repository, Phase5Service

router = APIRouter(tags=["phase5"])


def get_phase5_repository() -> Phase5Repository:
    raise ApiError(503, "PHASE5_DEPENDENCIES_UNAVAILABLE", "Phase 5 persistence is not integrated")


def get_phase5_service(
    repository: Annotated[Phase5Repository, Depends(get_phase5_repository)],
) -> Phase5Service:
    return Phase5Service(repository, SHARED_CALENDAR)


Service = Annotated[Phase5Service, Depends(get_phase5_service)]
IncidentId = Annotated[str, Path(alias="incidentId")]
ERRORS: dict[int | str, dict[str, Any]] = {
    400: {"description": "Invalid request"},
    401: {"description": "Unauthorized"},
    404: {"description": "Unknown incident"},
    409: {"description": "State conflict"},
    503: {"description": "Phase 5 persistence unavailable"},
}


@router.post(
    "/incidents/{incidentId}/corrections",
    status_code=201,
    response_model=DecisionCreated,
    responses=ERRORS,
)
def correct_decision(
    incident_id: IncidentId, data: CorrectionCreate, service: Service
) -> DecisionCreated:
    return service.correct_decision(incident_id, data)


@router.post(
    "/incidents/{incidentId}/filing",
    status_code=201,
    response_model=FilingCreated,
    responses=ERRORS,
)
def record_filing(incident_id: IncidentId, data: FilingCreate, service: Service) -> FilingCreated:
    return service.record_filing(incident_id, data)


@router.get("/incidents/{incidentId}/timeline", response_model=IncidentTimeline, responses=ERRORS)
def timeline(incident_id: IncidentId, service: Service) -> IncidentTimeline:
    return service.timeline(incident_id)
