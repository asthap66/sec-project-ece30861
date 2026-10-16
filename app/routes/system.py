"""System routes: GET /health and POST /reset.

Owner: Srihari (infrastructure).
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(tags=["system"])


class StatusResponse(BaseModel):
    status: str


@router.get("/health")
def health() -> StatusResponse:
    """Public (no API key): says the service is running (REQ-13, AC-14)."""
    return StatusResponse(status="OK")


@router.post("/reset")
def reset(db: Session = Depends(get_db)) -> StatusResponse:  # noqa: B008
    """Clear all stored test data so automated tests start from a known state (REQ-14).

    Needs the API key (the middleware checks it). Evidence and incidents are
    cleared in one statement inside one transaction, so a reset either fully
    happens or doesn't happen at all. RESTART IDENTITY also restarts the ID
    counters, so the next incident after a reset is INC-001 again; in
    PostgreSQL that restart is rolled back too if the transaction fails.
    """
    db.execute(text("TRUNCATE TABLE evidence, incidents RESTART IDENTITY"))
    db.commit()
    return StatusResponse(status="RESET_COMPLETE")
