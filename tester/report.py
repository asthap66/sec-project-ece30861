"""Turn recorded pytest results into the course's suite report.

Course spec, Tester section: outcomes pass/fail/error/skip; error results also
carry a source (tester, system, communication, unknown); every planned test
appears exactly once with a unique, nonempty test_id and a nonempty message;
coverage has code, component and system entries.
"""

import re
from typing import Any

# What counts as which acceptance criterion: the pod's AC-01..AC-16
# (Phase 2 - Pod.pdf, Q4). Matched against the test's function name.
AC_TOTAL = 16
_AC_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"test_ac(\d\d)_"), "{0}"),
    (re.compile(r"test_unknown_incident_get_is_404"), "03"),
    (re.compile(r"test_invalid_evidence_is_rejected"), "05"),
    (re.compile(r"test_stored_incident_cannot_be_edited_or_deleted"), "08"),
    (
        re.compile(
            r"test_(health_is_public|health_body_has_status|401_uses_error_format|"
            r"authenticated_route_|deployment_uses_https)"
        ),
        "14",
    ),
    (re.compile(r"test_reset_"), "16"),
]

# Exceptions meaning "no response came back": a communication problem (spec).
_COMMUNICATION = re.compile(
    r"(Timeout|ConnectError|ConnectTimeout|ReadTimeout|WriteTimeout|PoolTimeout|"
    r"RemoteProtocolError|NetworkError|ConnectionError)$"
)
# An assertion comparing a 5xx status with the expected one: the target reported
# an internal failure, which the spec counts as an error with source "system".
_SYSTEM_5XX = re.compile(r"\bassert (5\d\d) (==|in) ")


def acceptance_criterion(nodeid: str) -> str | None:
    name = nodeid.split("::")[-1]
    for pattern, template in _AC_RULES:
        match = pattern.search(name)
        if match:
            return "AC-" + template.format(*match.groups())
    return None


def test_id(nodeid: str) -> str:
    """tests/acceptance/test_x.py::test_name[param] -> test_name[param] (unique per suite)."""
    return nodeid.split("::")[-1]


def classify(record: dict[str, Any]) -> dict[str, Any]:
    """One pytest result -> one course result entry."""
    tid, outcome = test_id(record["nodeid"]), record["outcome"]
    message, exception = record.get("message") or "", record.get("exception") or ""
    if outcome == "passed":
        return {
            "test_id": tid,
            "outcome": "pass",
            "message": "Behaviour matched the pod specification.",
        }
    if outcome == "skipped":
        return {"test_id": tid, "outcome": "skip", "message": message or "Test was not executed."}
    if _COMMUNICATION.search(exception.split(".")[-1]):
        return {
            "test_id": tid,
            "outcome": "error",
            "source": "communication",
            "message": f"No response to evaluate ({exception}): {message}",
        }
    if outcome == "setup_error":
        return {
            "test_id": tid,
            "outcome": "error",
            "source": "tester",
            "message": f"Test setup failed in the tester: {message}",
        }
    if _SYSTEM_5XX.search(message):
        return {
            "test_id": tid,
            "outcome": "error",
            "source": "system",
            "message": f"The target reported an internal failure: {message}",
        }
    return {"test_id": tid, "outcome": "fail", "message": message or "Assertion failed."}


def build_report(
    session_id: str,
    target_url: str,
    planned: list[str],
    records: dict[str, dict[str, Any]],
    code_coverage: dict[str, Any],
    aborted: str | None = None,
) -> dict[str, Any]:
    """The complete suite report. Every planned test appears exactly once.

    aborted: if the run was cut short, why. Then the test that was running is an
    error with source "tester" and tests that never started are "skip" (spec).
    """
    results: list[dict[str, Any]] = []
    interrupted_marked = False
    for nodeid in planned:
        if nodeid in records:
            results.append(classify(records[nodeid]))
        elif aborted and not interrupted_marked:
            interrupted_marked = True
            results.append(
                {
                    "test_id": test_id(nodeid),
                    "outcome": "error",
                    "source": "tester",
                    "message": f"Not evaluated: the tester aborted ({aborted}).",
                }
            )
        else:
            results.append(
                {
                    "test_id": test_id(nodeid),
                    "outcome": "skip",
                    "message": "Not executed"
                    + (f": the tester aborted ({aborted})." if aborted else "."),
                }
            )

    exercised: set[str] = set()
    for nodeid in planned:
        criterion = acceptance_criterion(nodeid)
        if criterion and nodeid in records and records[nodeid]["outcome"] != "skipped":
            exercised.add(criterion)
    return {
        "session_id": session_id,
        "target_url": target_url,
        "results": results,
        "coverage": {
            "code": code_coverage,
            "component": {
                "covered": None,
                "total": None,
                "basis": "The pod specification (Phase 2) defines no component list, "
                "so component coverage can't be computed.",
            },
            "system": {
                "covered": len(exercised),
                "total": AC_TOTAL,
                "basis": "Acceptance criteria AC-01 to AC-16 in the pod specification; one "
                "counts as exercised when at least one test for it ran: "
                + (", ".join(sorted(exercised)) or "none")
                + ".",
            },
        },
    }
