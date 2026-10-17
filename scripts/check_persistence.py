"""AC-16 / REQ-15 restart persistence and reset check, in three steps.

Owner: Mohit. The restart itself happens between steps, outside this script
(e.g. `docker compose restart app`, or the host's restart button), so the same
script works locally and against a deployment.

    BASE_URL=... API_KEY=... uv run python -m scripts.check_persistence create --state run.json
    # restart the service WITHOUT calling /reset
    BASE_URL=... API_KEY=... uv run python -m scripts.check_persistence verify --state run.json
    # separately, destructive:
    ALLOW_DESTRUCTIVE_TESTS=1 ... uv run python -m scripts.check_persistence reset --state run.json

`verify` re-reads every incident created in `create` and compares the stored
values. `reset` calls POST /reset and confirms each of those incidents is gone
(404). Without a list route (docs/contract-issues.md #2) this is the closest
black-box check of "no incidents remain".

Exit code 0 = pass, 1 = fail, 2 = could not run.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from scripts.common import client_from_env, create_incidents, reset, run_conditions

TEXT_FIELDS = ("title", "description", "reporterName")


def compare(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    """Differences between what was created and what the service returns now."""
    problems = [
        f"{field}: expected {expected[field]!r}, got {actual.get(field)!r}"
        for field in TEXT_FIELDS
        if actual.get(field) != expected[field]
    ]
    try:
        same_instant = datetime.fromisoformat(actual["discoveredAt"]) == datetime.fromisoformat(
            expected["discoveredAt"]
        )
    except (KeyError, TypeError, ValueError):
        same_instant = False
    if not same_instant:
        problems.append(
            f"discoveredAt: expected {expected['discoveredAt']}, got {actual.get('discoveredAt')}"
        )
    return problems


def step_create(client: httpx.Client, state: Path, count: int) -> int:
    incidents = create_incidents(client, count)
    state.write_text(
        json.dumps(
            {"conditions": run_conditions(str(client.base_url)), "incidents": incidents}, indent=2
        ),
        encoding="utf-8",
    )
    print(f"created {len(incidents)} incidents; state saved to {state}")
    print("now restart the service (without /reset), then run the verify step")
    return 0


def step_verify(client: httpx.Client, incidents: list[dict[str, Any]]) -> int:
    failures = []
    for expected in incidents:
        incident_id = expected["incidentId"]
        response = client.get(f"/incidents/{incident_id}")
        if response.status_code != 200:
            failures.append(f"{incident_id}: GET returned {response.status_code}")
            continue
        failures += [f"{incident_id}: {p}" for p in compare(expected, response.json())]
    broken = {f.split(":")[0] for f in failures}
    print(f"verified {len(incidents) - len(broken)}/{len(incidents)} incidents intact")
    for failure in failures:
        print(f"  FAIL {failure}")
    return 1 if failures else 0


def step_reset(client: httpx.Client, incidents: list[dict[str, Any]]) -> int:
    reset(client)
    remaining = [
        i["incidentId"]
        for i in incidents
        if client.get(f"/incidents/{i['incidentId']}").status_code != 404
    ]
    print(f"after reset: {len(incidents) - len(remaining)}/{len(incidents)} incidents gone")
    for incident_id in remaining:
        print(f"  FAIL {incident_id} still retrievable")
    return 1 if remaining else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("step", choices=["create", "verify", "reset"])
    parser.add_argument("--state", type=Path, required=True, help="JSON file shared between steps")
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args(argv)

    with client_from_env() as client:
        if args.step == "create":
            return step_create(client, args.state, args.count)
        incidents = json.loads(args.state.read_text(encoding="utf-8"))["incidents"]
        if args.step == "verify":
            return step_verify(client, incidents)
        return step_reset(client, incidents)


if __name__ == "__main__":
    raise SystemExit(main())
