"""Per-session code coverage for the course testing interface.

Owner: Srihari (infrastructure).

GET /test/report returns the source lines of the app executed by the project
requests made in a session since its /test/setup (course spec, "System").
This uses coverage.py with dynamic contexts: /test/setup switches the context
to the session ID, so every line run afterwards is recorded under it, and the
report counts the lines recorded for that session.

On only when APP_COVERAGE=1 (the container sets it); tests and local runs
don't pay for it. If it's off or anything goes wrong, the report says so with
null counts and an explanation, as the spec asks, instead of a made-up zero.
Measurements live in memory, so a restart clears them; the service runs a
single instance so all requests of a session are measured in one place.
Requests are expected one at a time (the tester calls the API in order); a
/test/... request running at the same moment as a project request would
attribute that project request's lines to the interface instead.
"""

import logging
import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

logger = logging.getLogger("app.coverage")

APP_DIR = Path(__file__).resolve().parent
# This file is the instrumentation itself, not app behaviour, so it isn't counted.
OMIT = [str(Path(__file__).resolve())]
# Lines run while serving /test/... requests are recorded under this label, so
# reading the report (or setting up) never changes a session's measurements.
INTERFACE_CONTEXT = "__testing_interface__"
BASIS = "Source lines of the app package executed by project requests in this session since setup"


class SessionCoverage:
    def __init__(self) -> None:
        self._cov: Any = None
        self._lock = threading.Lock()
        self._unavailable = "measurement disabled (APP_COVERAGE is not 1)"
        self._current = INTERFACE_CONTEXT  # context project requests are recorded under
        self._interface_depth = 0

    def start(self) -> None:
        """Start measuring. Call once per process, before requests are served."""
        if os.environ.get("APP_COVERAGE") != "1" or self._cov is not None:
            return
        try:
            import coverage

            self._cov = coverage.Coverage(
                data_file=None, source=[str(APP_DIR)], omit=OMIT, concurrency=["thread"]
            )
            self._cov.start()
            self._unavailable = ""
            logger.info("code coverage measurement started")
        except Exception as exc:  # noqa: BLE001 - coverage must never stop the app
            self._cov = None
            self._unavailable = f"instrumentation failed to start ({type(exc).__name__})"
            logger.warning("code coverage unavailable: %s", exc)

    def begin_session(self, session_id: str) -> None:
        """Record project requests from now on under this session."""
        with self._lock:
            self._current = session_id
            if self._cov is not None and self._interface_depth == 0:
                self._cov.switch_context(session_id)

    @contextmanager
    def interface_request(self) -> Iterator[None]:
        """Wrap a /test/... request so its own lines aren't counted for the session."""
        if self._cov is None:
            yield
            return
        with self._lock:
            self._interface_depth += 1
            self._cov.switch_context(INTERFACE_CONTEXT)
        try:
            yield
        finally:
            with self._lock:
                self._interface_depth -= 1
                if self._interface_depth == 0:
                    self._cov.switch_context(self._current)

    def measure(self, session_id: str) -> dict[str, Any]:
        """{covered, total, basis} for one session (null counts if unavailable)."""
        if self._cov is None:
            return {"covered": None, "total": None, "basis": f"{BASIS}; {self._unavailable}"}
        try:
            with self._lock:
                data = self._cov.get_data()
                data.set_query_contexts([session_id])
                covered = total = 0
                for path in sorted(APP_DIR.rglob("*.py")):
                    if str(path) in OMIT:
                        continue
                    statements = set(self._cov.analysis2(str(path))[1])
                    total += len(statements)
                    covered += len(statements & set(data.lines(str(path)) or []))
                data.set_query_contexts(None)
            return {"covered": covered, "total": total, "basis": BASIS}
        except Exception as exc:  # noqa: BLE001
            logger.warning("code coverage measurement failed: %s", exc)
            return {
                "covered": None,
                "total": None,
                "basis": f"{BASIS}; measurement failed ({type(exc).__name__})",
            }


session_coverage = SessionCoverage()
