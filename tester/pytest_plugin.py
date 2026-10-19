"""pytest plugin the tester loads into each suite run (-p tester.pytest_plugin).

Writes one JSON line per event to the file in $TESTER_RESULTS_FILE as the run
goes, so if the run is cut short the results recorded so far survive (course
spec: "Keeps available results if the tester aborts").

Lines:
  {"event": "planned", "tests": [nodeid, ...]}       once, after collection
  {"event": "result", "nodeid", "outcome", "message", "exception"}   per test
"""

import json
import os
from typing import Any

import pytest

_FILE = os.environ.get("TESTER_RESULTS_FILE", "")
_seen: dict[str, str] = {}


def _write(record: dict[str, Any]) -> None:
    if _FILE:
        with open(_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


def _exception_name(report: pytest.TestReport) -> str:
    excinfo = getattr(report, "longrepr", None)
    crash = getattr(getattr(excinfo, "reprcrash", None), "message", "") or ""
    # reprcrash.message looks like "httpx.ReadTimeout: ..." or "AssertionError: ..."
    return crash.split(":", 1)[0].strip() if ":" in crash else ""


def _message(report: pytest.TestReport) -> str:
    crash = getattr(getattr(report, "longrepr", None), "reprcrash", None)
    text = getattr(crash, "message", "") or str(report.longrepr or "")
    return " ".join(text.split())[:500]


@pytest.hookimpl
def pytest_collection_finish(session: pytest.Session) -> None:
    _write({"event": "planned", "tests": [item.nodeid for item in session.items]})


@pytest.hookimpl
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    nodeid = report.nodeid
    if nodeid in _seen:
        return  # already recorded (e.g. setup failed, then teardown also reports)
    if report.when == "setup" and report.failed:
        outcome = "setup_error"
    elif report.when == "setup" and report.skipped:
        outcome = "skipped"
    elif report.when == "call":
        outcome = "passed" if report.passed else "skipped" if report.skipped else "failed"
    else:
        return
    _seen[nodeid] = outcome
    message = "" if outcome == "passed" else _message(report)
    if outcome == "skipped" and isinstance(report.longrepr, tuple):
        message = str(report.longrepr[2])  # the skip reason
    _write(
        {
            "event": "result",
            "nodeid": nodeid,
            "outcome": outcome,
            "message": message,
            "exception": _exception_name(report),
        }
    )
