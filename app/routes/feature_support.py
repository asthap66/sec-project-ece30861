"""Connect feature services to the shared request-scoped database dependency."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.incidents import IncidentService, SQLAlchemyIncidentRepository


def get_incident_service(session: Annotated[Session, Depends(get_db)]) -> IncidentService:
    return IncidentService(SQLAlchemyIncidentRepository(session))
