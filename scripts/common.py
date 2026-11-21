"""Shared helpers for the performance and persistence scripts.

Owner: Mohit. The target and key come from BASE_URL and API_KEY, never from
source code. Request bodies come from the shared fixtures in tests/fixtures/data/.
"""

import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "data"
API_KEY_HEADER = "X-API-Key"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def client_from_env(timeout: float = 10.0) -> httpx.Client:
    base_url = os.environ.get("BASE_URL", "").strip().rstrip("/")
    api_key = os.environ.get("API_KEY", "").strip()
    if not base_url or not api_key:
        fail("set BASE_URL and API_KEY")
    return httpx.Client(base_url=base_url, headers={API_KEY_HEADER: api_key}, timeout=timeout)


def require_destructive_opt_in(action: str) -> None:
    if os.environ.get("ALLOW_DESTRUCTIVE_TESTS") != "1":
        fail(f"{action} wipes the target; set ALLOW_DESTRUCTIVE_TESTS=1 to allow it")


def reset(client: httpx.Client) -> None:
    require_destructive_opt_in("POST /reset")
    response = client.post("/reset")
    if response.status_code != 200:
        fail(f"POST /reset returned {response.status_code}: {response.text}")


def fixture_bodies(filename: str) -> list[dict[str, Any]]:
    raw = json.loads((FIXTURES / filename).read_text(encoding="utf-8"))
    return [case["body"] for case in raw["cases"]]


def synthetic_incident(index: int) -> dict[str, Any]:
    """A valid incident body, varied by index so every record is distinguishable."""
    bodies = fixture_bodies("incidents_valid.json")
    body = dict(bodies[index % len(bodies)])
    body["title"] = f"[synthetic {index:03d}] {body['title']}"[:200]
    return body


def create_incidents(client: httpx.Client, count: int) -> list[dict[str, Any]]:
    """POST `count` incidents; return their bodies with the assigned incidentId."""
    created = []
    for index in range(count):
        body = synthetic_incident(index)
        response = client.post("/incidents", json=body)
        if response.status_code != 201:
            fail(f"POST /incidents #{index} returned {response.status_code}: {response.text}")
        created.append({**body, "incidentId": response.json()["incidentId"]})
    return created


def run_conditions(base_url: str) -> dict[str, str]:
    """Test conditions recorded with every result, so runs can be compared honestly."""
    try:
        commit = subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"
    return {
        "date": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "target": base_url,
        "client_commit": commit,
        "client_host": (
            f"{platform.system()} {platform.machine()}, Python {platform.python_version()}"
        ),
    }
