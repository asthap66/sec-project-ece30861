"""Shared deadline calendar (REQ-09, REQ-10; AC-09, AC-10, AC-11 overdue part).

Expected dates are copied from the Phase 2 contract (Q5.1 example, Model 3,
AC-09, AC-10), not computed with the code under test.
"""

from datetime import date, datetime

import pytest

from app.deadline_calendar import SHARED_CALENDAR, CalendarConfigError, DeadlineCalendar
from app.errors import ApiError
from app.holidays import FEDERAL_HOLIDAYS, HOLIDAYS_VERSION
from app.schemas import DeadlineState


@pytest.mark.parametrize(
    ("determined_at", "deadline", "source"),
    [
        ("2026-09-22T15:00:00-04:00", "2026-09-28", "Q5.1 decision example"),
        ("2026-09-28T10:00:00-04:00", "2026-10-02", "Model 3 example"),
        ("2025-09-29T12:00:00-04:00", "2025-10-03", "AC-09 standard"),
        ("2025-10-10T12:00:00-04:00", "2025-10-17", "AC-10 Columbus Day"),
        ("2025-11-25T12:00:00-05:00", "2025-12-02", "AC-10 Thanksgiving"),
        ("2025-12-30T12:00:00-05:00", "2026-01-06", "AC-10 New Year"),
        ("2025-10-04T12:00:00-04:00", "2025-10-09", "AC-10 Saturday determination"),
    ],
)
def test_reference_deadlines(determined_at: str, deadline: str, source: str) -> None:
    assert SHARED_CALENDAR.calculate_deadline(datetime.fromisoformat(determined_at)) == (
        date.fromisoformat(deadline)
    ), source


@pytest.mark.parametrize(
    ("determined_at", "deadline"),
    [
        # 2025-09-30 03:59:59Z is still Sep 29 in New York (EDT, UTC-4)
        ("2025-09-30T03:59:59Z", "2025-10-03"),
        # one second later it is Sep 30 there, so the deadline moves a day
        ("2025-09-30T04:00:00Z", "2025-10-06"),
        # winter: EST is UTC-5, so 04:59:59Z on Dec 1 is still Nov 30
        ("2025-12-01T04:59:59Z", "2025-12-04"),
        ("2025-12-01T05:00:00Z", "2025-12-05"),
    ],
)
def test_eastern_date_not_utc_date(determined_at: str, deadline: str) -> None:
    result = SHARED_CALENDAR.calculate_deadline(datetime.fromisoformat(determined_at))
    assert result == date.fromisoformat(deadline)


def test_equivalent_offsets_give_same_deadline() -> None:
    same = ["2025-09-29T12:00:00-04:00", "2025-09-29T16:00:00Z", "2025-09-29T21:30:00+05:30"]
    assert {SHARED_CALENDAR.calculate_deadline(datetime.fromisoformat(t)) for t in same} == {
        date(2025, 10, 3)
    }


@pytest.mark.parametrize(
    ("as_of", "status", "business_days"),
    [
        # Model 3: deadline 2026-10-02 (Friday)
        ("2026-09-28T12:00:00-04:00", DeadlineState.PENDING, 4),
        ("2026-10-01T12:00:00-04:00", DeadlineState.PENDING, 1),
        ("2026-10-02T23:59:59-04:00", DeadlineState.PENDING, 0),
        ("2026-10-03T00:00:00-04:00", DeadlineState.OVERDUE, 0),
        ("2026-10-05T12:00:00-04:00", DeadlineState.OVERDUE, 1),
        ("2026-10-06T12:00:00-04:00", DeadlineState.OVERDUE, 2),
    ],
)
def test_model3_status_and_business_days(
    as_of: str, status: DeadlineState, business_days: int
) -> None:
    result = SHARED_CALENDAR.describe_deadline(date(2026, 10, 2), datetime.fromisoformat(as_of))
    assert (result.status, result.deadline, result.business_days) == (
        status,
        date(2026, 10, 2),
        business_days,
    )


def test_ac11_overdue_without_filing() -> None:
    result = SHARED_CALENDAR.describe_deadline(
        date(2025, 10, 3), datetime.fromisoformat("2025-10-06T12:00:00Z")
    )
    assert result.status == DeadlineState.OVERDUE


def test_due_date_boundary_is_eastern_midnight() -> None:
    deadline = date(2025, 10, 3)
    last = SHARED_CALENDAR.describe_deadline(
        deadline, datetime.fromisoformat("2025-10-04T03:59:59Z")
    )
    first = SHARED_CALENDAR.describe_deadline(
        deadline, datetime.fromisoformat("2025-10-04T00:00:00-04:00")
    )
    assert (last.status, first.status) == (DeadlineState.PENDING, DeadlineState.OVERDUE)


def test_holiday_after_due_date_is_not_counted() -> None:
    # due Fri 2025-10-10; Mon Oct 13 is Columbus Day, so Tue Oct 14 is day 1 late
    late = SHARED_CALENDAR.describe_deadline(
        date(2025, 10, 10), datetime.fromisoformat("2025-10-14T09:00:00-04:00")
    )
    assert (late.status, late.business_days) == (DeadlineState.OVERDUE, 1)


def test_no_deadline_is_not_applicable() -> None:
    result = SHARED_CALENDAR.describe_deadline(None, datetime.fromisoformat("2026-10-01T00:00:00Z"))
    assert (result.status, result.deadline, result.business_days) == (
        DeadlineState.NOT_APPLICABLE,
        None,
        0,
    )


@pytest.mark.parametrize("moment", ["2024-12-31T12:00:00-05:00", "2028-01-03T12:00:00-05:00"])
def test_dates_outside_supported_years_are_refused(moment: str) -> None:
    with pytest.raises(ApiError) as caught:
        SHARED_CALENDAR.calculate_deadline(datetime.fromisoformat(moment))
    assert (caught.value.status_code, caught.value.code) == (400, "DATE_OUT_OF_RANGE")


def test_deadline_running_past_supported_years_is_refused() -> None:
    # Dec 29 2027 + 4 business days would land in January 2028
    with pytest.raises(ApiError):
        SHARED_CALENDAR.calculate_deadline(datetime.fromisoformat("2027-12-29T12:00:00-05:00"))


def test_naive_times_are_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        SHARED_CALENDAR.calculate_deadline(datetime(2025, 9, 29, 12))


def test_shipped_holiday_list_is_valid_and_versioned() -> None:
    days = [day for day, _ in FEDERAL_HOLIDAYS]
    assert days == sorted(days) and len(days) == len(set(days)) == 34
    assert all(day.weekday() < 5 for day in days)
    assert SHARED_CALENDAR.version == HOLIDAYS_VERSION


@pytest.mark.parametrize(
    ("holidays", "message"),
    [
        ([date(2025, 10, 13), date(2025, 10, 13)], "duplicate"),
        ([date(2025, 10, 11)], "weekend"),
        ([date(2024, 12, 25)], "outside"),
    ],
)
def test_invalid_holiday_lists_fail_at_startup(holidays: list[date], message: str) -> None:
    with pytest.raises(CalendarConfigError, match=message):
        DeadlineCalendar(holidays, first_year=2025, last_year=2027)
