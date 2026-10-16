"""Synthetic timestamp helpers and shared constants.

Owner: Mohit. Request bodies live in the JSON files under tests/fixtures/data/
(loaded by tests/fixtures/data.py).
"""

from datetime import UTC, datetime, timedelta

# Agreed in README section 4.
EVIDENCE_CATEGORIES = ("TECHNICAL", "BUSINESS_IMPACT", "LEGAL", "OTHER")

# A fixed instant well in the past, with an explicit UTC offset.
HISTORICAL_DISCOVERY = datetime(2024, 3, 14, 9, 30, tzinfo=UTC)


def iso(value: datetime) -> str:
    """RFC 3339 / ISO 8601 with a Z suffix, e.g. 2024-03-14T09:30:00Z."""
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def future_timestamp(days: int = 365) -> datetime:
    """Far enough ahead that clock skew cannot make it valid."""
    return datetime.now(UTC) + timedelta(days=days)
