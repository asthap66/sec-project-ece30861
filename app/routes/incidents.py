"""Append-only incident endpoints protected by the application's API-key middleware."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.routes.feature_support import get_incident_service
from app.schemas import IncidentCreate, IncidentCreated, IncidentDetail
from app.services.incidents import IncidentService

router = APIRouter()
Service = Annotated[IncidentService, Depends(get_incident_service)]


@router.post("/incidents", response_model=IncidentCreated, status_code=201)
def create_incident(data: IncidentCreate, service: Service) -> IncidentCreated:
    incident = service.create_incident(data)
    return IncidentCreated(incident_id=incident.incident_id, status=incident.status)


@router.get("/incidents/{incidentId}", response_model=IncidentDetail)
def get_incident(
    incident_id: Annotated[str, Path(alias="incidentId")], service: Service
) -> IncidentDetail:
    return service.get_incident(incident_id)
