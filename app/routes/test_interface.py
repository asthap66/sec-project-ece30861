"""System side of the course testing interface: POST /test/setup, GET /test/report.

Owner: Srihari (infrastructure). Spec: "Cross-team Testing Interface"
(student-facing-spec), section "System".

How sessions work here (documented for the pod in docs/cross-team-testing.md):
- /test/setup resets the project data to an empty baseline (like POST /reset),
  records the session ID, and starts measuring code coverage under it.
- One session is active at a time: the latest setup is the prepared state.
  Project requests don't carry the session ID; they act on that state.
- A session ID can be used once. Reusing one is 409, even after a restart.

Errors on these endpoints use the testing interface's format,
{"message": ..., "source": "system"}, not the project API's
{"error": ..., "message": ...}.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.coverage_runtime import session_coverage
from app.db import get_db
from app.models import TestSession

router = APIRouter(prefix="/test", tags=["testing interface"])
logger = logging.getLogger("app.test_interface")

SESSION_ID_MAX_LENGTH = 200


def interface_error(status_code: int, message: str) -> JSONResponse:
    """Error body for the testing-interface endpoints."""
    return JSONResponse(status_code=status_code, content={"message": message, "source": "system"})


class SetupRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=SESSION_ID_MAX_LENGTH)
    # Pod-defined starting data. Our pod defines none, so {} (an object is required).
    setup: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    session_id: str


@router.post("/setup", status_code=201, response_model=SessionResponse)
async def test_setup(request: Request, db: Session = Depends(get_db)) -> Any:  # noqa: B008
    """Prepare a clean state for a test session and return its ID when ready."""
    try:
        body = SetupRequest.model_validate(await request.json())
    except (ValueError, ValidationError):
        return interface_error(
            400, 'body must be {"session_id": "<non-empty string>", "setup": {}}'
        )
    if not body.session_id.strip():
        return interface_error(400, "session_id must not be blank")

    if db.get(TestSession, body.session_id) is not None:
        return interface_error(409, f"session {body.session_id} already exists")
    try:
        # One transaction: record the session and clear the project data, so
        # either both happen or neither does.
        db.add(TestSession(session_id=body.session_id))
        db.execute(text("TRUNCATE TABLE evidence, incidents RESTART IDENTITY"))
        db.commit()
    except IntegrityError:
        db.rollback()  # the same ID was set up concurrently
        return interface_error(409, f"session {body.session_id} already exists")
    except Exception:
        db.rollback()
        logger.exception("test setup failed")
        return interface_error(500, "could not initialize the session database")

    session_coverage.begin_session(body.session_id)
    return SessionResponse(session_id=body.session_id)


@router.get("/report")
def test_report(
    session_id: str = Query(default="", max_length=SESSION_ID_MAX_LENGTH),
    db: Session = Depends(get_db),  # noqa: B008
) -> Any:
    """Code coverage measured for this session so far. Runs no project operations."""
    if not session_id:
        return interface_error(400, "session_id query parameter is required")
    if (
        db.scalar(select(TestSession.session_id).where(TestSession.session_id == session_id))
        is None
    ):
        return interface_error(404, f"unknown session {session_id}")
    return {"session_id": session_id, "coverage": {"code": session_coverage.measure(session_id)}}
