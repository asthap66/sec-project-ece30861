"""Filing deadlines and deadline status (REQ-09, REQ-10).

Owner: Srihari. This is the one calendar used by every endpoint; Astha's
DecisionService calls it through the DeadlineCalculator protocol.

Rules (Phase 2 contract, Model 3 and AC-09/AC-10/AC-11):
- A time becomes a date in US Eastern time (America/New_York, so EST/EDT
  is handled; never a fixed UTC-4 offset).
- The deadline is the 4th business day AFTER the determination's Eastern
  date. The determination date itself is day 0.
- Business days are Monday-Friday that are not in app.holidays.
- PENDING through the whole Eastern due date, OVERDUE from the next day.
- businessDays: for PENDING, business days left after the as_of date up to
  and including the due date (0 on the due date). For OVERDUE, business days
  after the due date up to and including the as_of date. Model 3 example:
  deadline 2026-10-02 gives PENDING 1 on Oct 1, OVERDUE 1 on Oct 5,
  OVERDUE 2 on Oct 6.
- No deadline (no decision, or NOT_MATERIAL) is NOT_APPLICABLE with
  businessDays 0. The contract doesn't fix this value (contract issue).

Dates outside the supported years are refused with a 400 instead of being
counted against a holiday list that doesn't cover them.
"""

from collections.abc import Iterable
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.errors import ApiError
from app.holidays import FEDERAL_HOLIDAYS, HOLIDAYS_VERSION, SUPPORTED_YEARS
from app.schemas import DeadlineState, DeadlineStatus

EASTERN = ZoneInfo("America/New_York")
BUSINESS_DAYS_TO_DEADLINE = 4


class CalendarConfigError(ValueError):
    """The holiday list itself is invalid; raised when the calendar is built."""


def eastern_date(moment: datetime) -> date:
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("calendar inputs must be timezone-aware")
    return moment.astimezone(EASTERN).date()


class DeadlineCalendar:
    """Business-day arithmetic over one validated holiday list."""

    def __init__(
        self,
        holidays: Iterable[date],
        first_year: int,
        last_year: int,
        version: str = "custom",
    ) -> None:
        listed = list(holidays)
        if first_year > last_year:
            raise CalendarConfigError("first supported year is after the last")
        if len(set(listed)) != len(listed):
            raise CalendarConfigError("holiday list has duplicate dates")
        for day in listed:
            if day.weekday() >= 5:
                raise CalendarConfigError(f"holiday {day} falls on a weekend")
            if not first_year <= day.year <= last_year:
                raise CalendarConfigError(f"holiday {day} is outside {first_year}-{last_year}")
        self.holidays = frozenset(listed)
        self.first_year = first_year
        self.last_year = last_year
        self.version = version

    def _check_range(self, day: date) -> None:
        if not self.first_year <= day.year <= self.last_year:
            raise ApiError(
                400,
                "DATE_OUT_OF_RANGE",
                f"deadline calendar covers {self.first_year}-{self.last_year} only; got {day}",
            )

    def is_business_day(self, day: date) -> bool:
        self._check_range(day)
        return day.weekday() < 5 and day not in self.holidays

    def _business_days_between(self, start: date, end: date) -> int:
        """Business days in (start, end]: after start, up to and including end."""
        count, day = 0, start
        while day < end:
            day += timedelta(days=1)
            if self.is_business_day(day):
                count += 1
        return count

    def calculate_deadline(self, determined_at: datetime) -> date:
        day = eastern_date(determined_at)
        self._check_range(day)
        counted = 0
        while counted < BUSINESS_DAYS_TO_DEADLINE:
            day += timedelta(days=1)
            if self.is_business_day(day):
                counted += 1
        return day

    def describe_deadline(self, deadline: date | None, as_of: datetime) -> DeadlineStatus:
        if deadline is None:
            return DeadlineStatus(
                status=DeadlineState.NOT_APPLICABLE, deadline=None, business_days=0
            )
        today = eastern_date(as_of)
        self._check_range(today)
        if today <= deadline:
            return DeadlineStatus(
                status=DeadlineState.PENDING,
                deadline=deadline,
                business_days=self._business_days_between(today, deadline),
            )
        return DeadlineStatus(
            status=DeadlineState.OVERDUE,
            deadline=deadline,
            business_days=self._business_days_between(deadline, today),
        )


SHARED_CALENDAR = DeadlineCalendar(
    (day for day, _name in FEDERAL_HOLIDAYS),
    first_year=SUPPORTED_YEARS[0],
    last_year=SUPPORTED_YEARS[1],
    version=HOLIDAYS_VERSION,
)
