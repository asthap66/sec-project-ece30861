"""The holiday list the deadline calendar skips (REQ-09).

Owner: Srihari. Versioned with the code: a change to this list is a code
change, reviewed and released like any other, and HOLIDAYS_VERSION goes in
test reports so a result can be traced to the list it used.

Source: US federal holidays under 5 U.S.C. 6103, as observed by federal
offices (a Saturday holiday is observed the Friday before, a Sunday holiday
the Monday after), from OPM's published federal holiday schedules. The pod
model (Phase 2, Model 3) listed 2026-2027 only; 2025 is added because AC-09
and AC-10 use 2025 dates. Every AC-09/AC-10 example needs exactly these
dates (Oct 13 2025, Nov 27 2025, Jan 1 2026). One-off closures, such as
days of mourning or extra days off by executive order, are not included.
The pod still has to confirm 2025 (contract issue logged in docs/phase4).

Dates outside SUPPORTED_YEARS are refused rather than guessed.
"""

from datetime import date

HOLIDAYS_VERSION = "us-federal-2025-2027.v1"
SUPPORTED_YEARS = (2025, 2027)

FEDERAL_HOLIDAYS: tuple[tuple[date, str], ...] = (
    (date(2025, 1, 1), "New Year's Day"),
    (date(2025, 1, 20), "Martin Luther King Jr. Day"),
    (date(2025, 2, 17), "Washington's Birthday"),
    (date(2025, 5, 26), "Memorial Day"),
    (date(2025, 6, 19), "Juneteenth"),
    (date(2025, 7, 4), "Independence Day"),
    (date(2025, 9, 1), "Labor Day"),
    (date(2025, 10, 13), "Columbus Day"),
    (date(2025, 11, 11), "Veterans Day"),
    (date(2025, 11, 27), "Thanksgiving Day"),
    (date(2025, 12, 25), "Christmas Day"),
    (date(2026, 1, 1), "New Year's Day"),
    (date(2026, 1, 19), "Martin Luther King Jr. Day"),
    (date(2026, 2, 16), "Washington's Birthday"),
    (date(2026, 5, 25), "Memorial Day"),
    (date(2026, 6, 19), "Juneteenth"),
    (date(2026, 7, 3), "Independence Day (observed)"),
    (date(2026, 9, 7), "Labor Day"),
    (date(2026, 10, 12), "Columbus Day"),
    (date(2026, 11, 11), "Veterans Day"),
    (date(2026, 11, 26), "Thanksgiving Day"),
    (date(2026, 12, 25), "Christmas Day"),
    (date(2027, 1, 1), "New Year's Day"),
    (date(2027, 1, 18), "Martin Luther King Jr. Day"),
    (date(2027, 2, 15), "Washington's Birthday"),
    (date(2027, 5, 31), "Memorial Day"),
    (date(2027, 6, 18), "Juneteenth (observed)"),
    (date(2027, 7, 5), "Independence Day (observed)"),
    (date(2027, 9, 6), "Labor Day"),
    (date(2027, 10, 11), "Columbus Day"),
    (date(2027, 11, 11), "Veterans Day"),
    (date(2027, 11, 25), "Thanksgiving Day"),
    (date(2027, 12, 24), "Christmas Day (observed)"),
    (date(2027, 12, 31), "New Year's Day 2028 (observed)"),
)
