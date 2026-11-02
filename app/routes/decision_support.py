"""FastAPI dependency boundary for Srihari's storage and calendar adapters."""

from typing import Annotated

from fastapi import Depends

from app.errors import ApiError
from app.services.decisions import DeadlineCalculator, DecisionRepository, DecisionService


def get_decision_repository() -> DecisionRepository | None:
    """Integration hook: override with an adapter using Depends(get_db).

    None means the adapter has not been connected, never an in-memory fallback.
    """
    return None


def get_deadline_calculator() -> DeadlineCalculator | None:
    """Integration hook for the single shared calendar implementation."""
    return None


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
