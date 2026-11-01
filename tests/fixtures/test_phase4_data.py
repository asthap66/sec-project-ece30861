"""Validate manual oracle data without importing the production calculator."""

import json
from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def test_manual_phase4_calendar_data() -> None:
    cases = json.loads((Path(__file__).parent / "data/phase4_deadlines.json").read_text())
    assert len({case["name"] for case in cases}) == len(cases) == 7
    for case in cases:
        instant = datetime.fromisoformat(case["determinedAt"])
        assert instant.utcoffset() is not None
        assert datetime(2024, 3, 14, tzinfo=UTC) < instant < datetime(2026, 1, 1, tzinfo=UTC)
        days = [date.fromisoformat(day) for day in case["countedDates"]]
        assert len(days) == len(set(days)) == 4
        assert days == sorted(days)
        assert days[0] > instant.astimezone(ZoneInfo("America/New_York")).date()
        assert all(day.weekday() < 5 for day in days)
        assert days[-1].isoformat() == case["deadline"]
        assert case["source"]
