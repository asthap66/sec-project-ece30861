"""Validate manual oracle data without importing the production calculator."""

import json
from copy import deepcopy
from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from tests.acceptance.client import AcceptanceConfig, ApiClient
from tests.acceptance.test_phase4_decisions import CALENDAR, INVALID, setup_decision
from tests.fixtures.data import VALID_INCIDENTS


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


def test_phase4_setup_chronology_and_shared_fixture_isolation() -> None:
    """Exercise actual setup requests; this does not simulate decision functionality."""
    original = deepcopy(VALID_INCIDENTS)
    discoveries: list[datetime] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        if request.url.path == "/incidents":
            discoveries.append(datetime.fromisoformat(body["discoveredAt"]))
            return httpx.Response(201, json={"incidentId": "INC-returned", "status": "OPEN"})
        assert request.url.path == "/incidents/INC-returned/evidence"
        return httpx.Response(
            201, json={"evidenceId": "EVD-returned", "recordedAt": "2026-01-01T00:00:00Z"}
        )

    client = ApiClient(
        AcceptanceConfig(base_url="https://api.example.test", api_key="test-key"),
        transport=httpx.MockTransport(handler),
    )
    try:
        _, payload = setup_decision(client)
        setup_decision(client)
    finally:
        client.close()
    assert original == VALID_INCIDENTS
    assert len(discoveries) == 2
    assert all(discovery == datetime(2020, 1, 1, tzinfo=UTC) for discovery in discoveries)
    valid_times = [case["determinedAt"] for case in CALENDAR] + [
        payload["determinedAt"],
        "2026-09-28T10:00:00-04:00",
    ]
    for value in valid_times:
        assert discoveries[0] < datetime.fromisoformat(value) < datetime.now(UTC)
    before = next(value for name, _, value in INVALID if name == "before-discovery")
    assert isinstance(before, str)
    assert datetime.fromisoformat(before) < discoveries[0]
