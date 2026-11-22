"""Guard independent Phase 5 scenario oracles before they reach route tests."""

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest

pytestmark = pytest.mark.phase5

SCENARIOS = json.loads((Path(__file__).parent / "data/phase5_scenarios.json").read_text())


def _instant(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    assert result.utcoffset() is not None
    return result


def test_decision_fixture_chronology_and_distinct_versions() -> None:
    incident = SCENARIOS["incident"]
    discovered = _instant(incident["discoveredAt"])
    original = incident["originalDecision"]
    corrected = incident["correctedDecision"]
    assert discovered < _instant(original["determinedAt"]) < _instant(corrected["determinedAt"])
    assert original["decision"] == "MATERIAL"
    assert corrected["decision"] == "NOT_MATERIAL"
    assert original["rationale"] != corrected["rationale"]
    assert date.fromisoformat(incident["deadline"]) == date(2025, 10, 3)


@pytest.mark.parametrize(
    "case", SCENARIOS["filingCases"], ids=[case["name"] for case in SCENARIOS["filingCases"]]
)
def test_filing_date_oracles_use_eastern_calendar_date(case: dict[str, Any]) -> None:
    deadline = date.fromisoformat(SCENARIOS["incident"]["deadline"])
    filed_date = _instant(case["filedAt"]).astimezone(ZoneInfo("America/New_York")).date()
    assert case["timeliness"] == ("ON_TIME" if filed_date <= deadline else "LATE")
    assert type(case["businessDaysLate"]) is int
    assert (
        case["businessDaysLate"]
        == {
            "before-deadline": 0,
            "on-deadline": 0,
            "end-of-deadline": 0,
            "after-deadline": 0,
            "after-business-day": 1,
        }[case["name"]]
    )
    assert _instant(case["filedAt"]) < datetime.now(UTC)


def test_invalid_scenarios_and_history_are_complete_and_ordered() -> None:
    assert set(SCENARIOS["invalidScenarios"]) == {
        "filing-without-material-decision",
        "duplicate-filing",
        "malformed-filing-timestamp",
        "unknown-incident",
        "unknown-evidence-on-correction",
    }
    events = SCENARIOS["historyOrder"]
    assert [event["kind"] for event in events] == [
        "incident",
        "evidence",
        "decision",
        "correction",
        "filing",
    ]
    instants = [_instant(event["at"]) for event in events]
    assert instants == sorted(instants)
    assert len(instants) == len(set(instants))
    assert SCENARIOS["persistence"]["afterRestart"]
    assert SCENARIOS["persistence"]["afterReset"]
