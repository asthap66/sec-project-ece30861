"""Tester web service: POST /test/setup, POST /test/run, GET /test/report.

Owner: Srihari. Spec: "Cross-team Testing Interface" (student-facing-spec),
Tester section and Execution rules.

Configuration (environment):
  ALLOWED_TARGETS   comma-separated system base URLs this tester may target
                    (approved pod services only; anything else is 400)
  TARGET_API_KEYS   JSON {"<base url>": "<key>"} for targets' X-API-Key
  TARGET_API_KEY    key used for targets not in TARGET_API_KEYS
  SETUP_TIMEOUT     seconds to wait for system setup (default 60)
  RUN_TIMEOUT       seconds for the whole suite (default 600)

Sessions and reports live in memory: they last until this instance stops, as
the spec allows. Deploy with a single instance.
"""

import json
import logging
import os
import threading
import uuid
from typing import Any
from urllib.parse import urlsplit

import anyio
import httpx
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from tester.report import build_report
from tester.runner import code_coverage, run_suite

logger = logging.getLogger("tester")
app = FastAPI(title="Incident API tester (course testing interface)", version="0.1.0")

_sessions: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


def _settings() -> dict[str, Any]:
    allowed = [u.strip().rstrip("/") for u in os.environ.get("ALLOWED_TARGETS", "").split(",")]
    try:
        keys = json.loads(os.environ.get("TARGET_API_KEYS", "") or "{}")
    except ValueError:
        keys = {}
    return {
        "allowed": [u for u in allowed if u],
        "keys": {k.rstrip("/"): v for k, v in keys.items()},
        "default_key": os.environ.get("TARGET_API_KEY", ""),
        "setup_timeout": float(os.environ.get("SETUP_TIMEOUT", "60")),
        "run_timeout": float(os.environ.get("RUN_TIMEOUT", "600")),
    }


def _http_client(timeout: float) -> httpx.AsyncClient:
    """The client used to call target systems (tests replace this one function)."""
    return httpx.AsyncClient(timeout=timeout)


def error(status: int, message: str, source: str = "tester") -> JSONResponse:
    return JSONResponse(status_code=status, content={"message": message, "source": source})


def _target_problem(target_url: Any, allowed: list[str]) -> str | None:
    if not isinstance(target_url, str) or not target_url.strip():
        return 'body must be {"target_url": "<system base URL>"}'
    parts = urlsplit(target_url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return "target_url must be an http(s) URL"
    if parts.query or parts.fragment or parts.username or parts.password:
        return "target_url must have no query, fragment or credentials"
    if target_url.rstrip("/").endswith("/test"):
        return "target_url is the system base URL, without /test"
    if target_url.rstrip("/") not in allowed:
        return "target_url is not an approved pod service URL for this tester"
    return None


@app.get("/", include_in_schema=False)
def index() -> dict[str, Any]:
    """Landing page for the registry's tester base URL, which otherwise 404s."""
    return {
        "service": app.title,
        "docs": "/docs",
        "endpoints": ["GET /health", "POST /test/setup", "POST /test/run", "GET /test/report"],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}


@app.post("/test/setup", status_code=201)
async def test_setup(request: Request) -> Any:
    """Create a session, have the target prepare it, return the ID once ready."""
    settings = _settings()
    try:
        body = await request.json()
    except ValueError:
        return error(400, "request body must be JSON")
    target = body.get("target_url") if isinstance(body, dict) else None
    problem = _target_problem(target, settings["allowed"])
    if problem or not isinstance(target, str):
        return error(400, problem or "target_url is required")
    target_url = target.rstrip("/")
    key = settings["keys"].get(target_url, settings["default_key"])
    session_id = str(uuid.uuid4())

    try:
        async with _http_client(settings["setup_timeout"]) as client:
            response = await client.post(
                f"{target_url}/test/setup",
                json={"session_id": session_id, "setup": {}},
                headers={"X-API-Key": key},
            )
    except httpx.HTTPError as exc:
        return error(
            500,
            f"Could not reach the system's /test/setup ({type(exc).__name__}).",
            source="communication",
        )

    if response.status_code != 201:
        # forward the system's failure: same status, message and source (spec)
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        payload = payload if isinstance(payload, dict) else {}
        message = payload.get("message") or response.text[:300] or "system setup failed"
        source = payload.get("source") or "system"
        return error(response.status_code, str(message), source=str(source))
    try:
        returned = response.json().get("session_id")
    except (ValueError, AttributeError):
        returned = None
    if returned != session_id:
        return error(500, "The system's setup returned a different session ID.", source="system")

    with _lock:
        _sessions[session_id] = {
            "target_url": target_url,
            "key": key,
            "state": "ready",
            "report": None,
        }
    logger.info("session %s ready for %s", session_id, target_url)
    return {"session_id": session_id}


@app.post("/test/run")
async def test_run(request: Request) -> Any:
    """Run the whole suite once for a prepared session and return its report."""
    try:
        body = await request.json()
    except ValueError:
        return error(400, "request body must be JSON")
    session_id = body.get("session_id") if isinstance(body, dict) else None
    if not isinstance(session_id, str) or not session_id:
        return error(400, 'body must be {"session_id": "<id from /test/setup>"}')
    with _lock:
        session = _sessions.get(session_id)
        if session is None:
            return error(404, f"unknown session {session_id}")
        if session["state"] != "ready":
            return error(409, f"session {session_id} has already been run ({session['state']})")
        session["state"] = "running"

    # the suite runs in a separate process; don't block the event loop meanwhile
    return await anyio.to_thread.run_sync(_run_and_store, session_id, session)


def _run_and_store(session_id: str, session: dict[str, Any]) -> JSONResponse:
    settings = _settings()
    target_url, key = session["target_url"], session["key"]
    aborted: str | None
    try:
        suite = run_suite(target_url, key, settings["run_timeout"])
        coverage = code_coverage(target_url, key, session_id, settings["setup_timeout"])
        report = build_report(
            session_id, target_url, suite.planned, suite.records, coverage, aborted=suite.aborted
        )
        aborted = suite.aborted
    except Exception as exc:  # noqa: BLE001 - must still store and return something
        logger.exception("tester aborted")
        aborted = f"internal error ({type(exc).__name__})"
        unavailable = {"covered": None, "total": None, "basis": "not collected: the tester aborted"}
        report = build_report(session_id, target_url, [], {}, unavailable, aborted=aborted)
    with _lock:  # store before responding (spec)
        session["report"] = report
        session["state"] = "aborted" if aborted else "done"
    if aborted:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"The tester aborted: {aborted}. Retrieve available results with "
                f"GET /test/report?session_id={session_id}.",
                "source": "tester",
            },
        )
    return JSONResponse(status_code=200, content=report)


@app.get("/test/report")
def test_report(session_id: str = Query(default="")) -> Any:
    """The stored report. Runs nothing; 409 until the suite has ended."""
    if not session_id:
        return error(400, "session_id query parameter is required")
    with _lock:
        session = _sessions.get(session_id)
        if session is None:
            return error(404, f"unknown session {session_id}")
        if session["report"] is None:
            return error(409, f"session {session_id} has not finished; try again later")
        return session["report"]


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
