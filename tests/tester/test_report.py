"""Report building: outcomes, sources, coverage, aborts (course spec, Tester section)."""

from typing import Any

from tester.report import AC_TOTAL, acceptance_criterion, build_report, classify

F = "tests/acceptance/test_ac01_05_incidents_evidence.py::"
S = "tests/acceptance/test_ac14_security.py::"
CODE = {"covered": 60, "total": 522, "basis": "lines"}


def record(nodeid: str, outcome: str, message: str = "", exception: str = "") -> dict[str, Any]:
    return {"nodeid": nodeid, "outcome": outcome, "message": message, "exception": exception}


def test_acceptance_criteria_mapping() -> None:
    assert acceptance_criterion(F + "test_ac01_create_then_retrieve[x]") == "AC-01"
    assert acceptance_criterion(F + "test_ac05_evidence_is_stored[y]") == "AC-05"
    assert (
        acceptance_criterion(F + "test_stored_incident_cannot_be_edited_or_deleted[PUT]") == "AC-08"
    )
    assert acceptance_criterion(S + "test_health_is_public") == "AC-14"
    assert acceptance_criterion("x.py::test_reset_succeeds_and_is_repeatable") == "AC-16"
    assert acceptance_criterion("x.py::test_something_else") is None


def test_outcomes_follow_the_spec() -> None:
    assert classify(record(F + "test_a", "passed"))["outcome"] == "pass"
    assert classify(record(F + "test_a", "skipped", "no key"))["outcome"] == "skip"
    failed = classify(record(F + "test_a", "failed", "assert 400 == 201", "AssertionError"))
    assert failed["outcome"] == "fail" and "source" not in failed


def test_no_response_is_a_communication_error() -> None:
    result = classify(record(F + "test_a", "failed", "timed out", "httpx.ReadTimeout"))
    assert result["outcome"] == "error" and result["source"] == "communication"


def test_target_5xx_is_a_system_error() -> None:
    result = classify(record(F + "test_a", "failed", "assert 500 == 201", "AssertionError"))
    assert result["outcome"] == "error" and result["source"] == "system"


def test_fixture_failure_is_a_tester_error() -> None:
    result = classify(record(F + "test_a", "setup_error", "fixture broke", "RuntimeError"))
    assert result["outcome"] == "error" and result["source"] == "tester"


def test_every_planned_test_appears_once_with_a_message() -> None:
    planned = [F + "test_ac01_a[1]", F + "test_ac01_a[2]", S + "test_health_is_public"]
    records = {p: record(p, "passed") for p in planned}
    report = build_report("run-1", "https://t", planned, records, CODE)
    ids = [r["test_id"] for r in report["results"]]
    assert len(ids) == len(set(ids)) == 3
    assert all(r["message"] for r in report["results"])
    assert report["session_id"] == "run-1" and report["target_url"] == "https://t"


def test_abort_marks_running_test_error_and_rest_skip() -> None:
    planned = [F + "test_ac01_a", F + "test_ac02_b", F + "test_ac03_c"]
    records = {planned[0]: record(planned[0], "passed")}
    report = build_report("run-1", "https://t", planned, records, CODE, aborted="timeout")
    outcomes = [(r["outcome"], r.get("source")) for r in report["results"]]
    assert outcomes == [("pass", None), ("error", "tester"), ("skip", None)]


def test_coverage_fields() -> None:
    planned = [F + "test_ac01_a", F + "test_ac03_b", S + "test_health_is_public", F + "test_ac04_c"]
    records = {p: record(p, "passed") for p in planned[:3]}
    records[planned[3]] = record(planned[3], "skipped", "no key")
    coverage = build_report("r", "https://t", planned, records, CODE)["coverage"]
    assert coverage["code"] == CODE
    # pod spec defines no components: null with a reason, never a substituted 0
    assert coverage["component"]["covered"] is None and coverage["component"]["basis"]
    system = coverage["system"]
    assert (system["covered"], system["total"]) == (3, AC_TOTAL)  # skipped AC-04 not counted
    assert "AC-01" in system["basis"] and "AC-04" not in system["basis"]
