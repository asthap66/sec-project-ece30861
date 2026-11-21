"""Connect feature services to the shared request-scoped database dependency."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.routes.decision_support import get_optional_decision_service
from app.services.decisions import DecisionService
from app.services.incidents import IncidentService, SQLAlchemyIncidentRepository


def get_incident_service(
    session: Annotated[Session, Depends(get_db)],
    decisions: Annotated[DecisionService | None, Depends(get_optional_decision_service)],
) -> IncidentService:
    return IncidentService(SQLAlchemyIncidentRepository(session), decisions)
