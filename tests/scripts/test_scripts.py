"""Self-tests for the performance and persistence scripts (no service; runs in CI)."""

import pytest

from scripts.check_persistence import compare
from scripts.common import synthetic_incident
from scripts.performance import Sample, build_plan, summarize


def test_summary_passes_at_exactly_95_percent() -> None:
    samples = [Sample("GET incident", 200, 0.01)] * 95 + [Sample("GET incident", 200, 1.5)] * 5
    summary = summarize(samples, threshold=1.0, required_share=0.95)
    assert summary["share_within_threshold"] == 0.95
    assert summary["passed"] is True


def test_summary_counts_errors_as_misses_even_when_fast() -> None:
    samples = [Sample("GET incident", 200, 0.01)] * 94 + [Sample("GET incident", 500, 0.01)] * 6
    summary = summarize(samples, threshold=1.0, required_share=0.95)
    assert summary["errors"] == 6
    assert summary["passed"] is False


def test_summary_rejects_empty_run() -> None:
    with pytest.raises(ValueError):
        summarize([], threshold=1.0, required_share=0.95)


def test_plan_has_requested_size_mix_and_is_reproducible() -> None:
    plan = build_plan(["INC-1", "INC-2"], total=200, seed=1)
    ops = [op for op, _, _ in plan]
    assert len(plan) == 200
    assert (ops.count("GET incident"), ops.count("POST evidence"), ops.count("GET health")) == (
        150,
        40,
        10,
    )
    assert plan == build_plan(["INC-1", "INC-2"], total=200, seed=1)


def test_synthetic_incidents_are_distinct_and_valid_length() -> None:
    titles = {synthetic_incident(i)["title"] for i in range(100)}
    assert len(titles) == 100
    assert all(0 < len(t) <= 200 for t in titles)


def test_compare_accepts_same_instant_in_utc() -> None:
    expected = synthetic_incident(0)  # discoveredAt has a -04:00 offset
    actual = {**expected, "discoveredAt": "2026-09-21T18:30:00Z"}
    assert compare(expected, actual) == []


def test_compare_reports_changed_fields() -> None:
    expected = synthetic_incident(0)
    actual = {**expected, "title": "changed", "discoveredAt": "2020-01-01T00:00:00Z"}
    problems = compare(expected, actual)
    assert len(problems) == 2
