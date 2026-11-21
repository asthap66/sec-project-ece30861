"""FastAPI dependency boundary for Srihari's storage and calendar adapters."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deadline_calendar import SHARED_CALENDAR
from app.errors import ApiError
from app.services.decision_store import SQLAlchemyDecisionRepository
from app.services.decisions import DeadlineCalculator, DecisionRepository, DecisionService


def get_decision_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DecisionRepository | None:
    """PostgreSQL decisions on the request's shared session (never a second one)."""
    return SQLAlchemyDecisionRepository(session)


def get_deadline_calculator() -> DeadlineCalculator | None:
    """The single shared calendar (app.deadline_calendar, app.holidays)."""
    return SHARED_CALENDAR


def get_optional_decision_service(
    repository: Annotated[DecisionRepository | None, Depends(get_decision_repository)],
    calendar: Annotated[DeadlineCalculator | None, Depends(get_deadline_calculator)],
) -> DecisionService | None:
    if repository is None and calendar is None:
        return None
    if repository is None or calendar is None:
        raise ApiError(
            503, "PHASE4_DEPENDENCIES_UNAVAILABLE", "Both Phase 4 adapters must be connected"
        )
    return DecisionService(repository, calendar)


def get_decision_service(
    service: Annotated[DecisionService | None, Depends(get_optional_decision_service)],
) -> DecisionService:
    if service is None:
        raise ApiError(
            503,
            "PHASE4_DEPENDENCIES_UNAVAILABLE",
            "Decision persistence and calendar adapters must be connected",
        )
    return service
