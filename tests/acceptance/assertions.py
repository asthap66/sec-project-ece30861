"""Shared assertions for acceptance tests, written from the pod contract (Q5)."""

from datetime import datetime, timedelta

import httpx


def assert_error_body(response: httpx.Response, status: int) -> dict[str, str]:
    """Contract: every error is {"error": "ERROR_CODE", "message": "..."}."""
    assert response.status_code == status, response.text
    body: dict[str, str] = response.json()
    assert isinstance(body.get("error"), str) and body["error"], body
    assert isinstance(body.get("message"), str) and body["message"], body
    return body


def _squash(text: str) -> str:
    return text.replace("_", "").replace(" ", "").lower()


def assert_names_field(body: dict[str, str], field: str) -> None:
    """REQ-02/AC-02: a 400 names the bad field (in the code or the message, any case)."""
    haystack = _squash(body["error"] + body["message"])
    assert _squash(field) in haystack, f"error does not name {field!r}: {body}"


def assert_utc_instant(actual: str, expected: str) -> None:
    """Contract: response timestamps are UTC and keep the submitted instant."""
    parsed = datetime.fromisoformat(actual)
    assert parsed.utcoffset() == timedelta(0), f"{actual} is not UTC"
    assert parsed == datetime.fromisoformat(expected), f"{actual} != {expected}"
