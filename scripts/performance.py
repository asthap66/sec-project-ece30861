"""AC-16 / REQ-15 response-time check.

Owner: Mohit. Loads synthetic incidents, then times a fixed mix of requests one
at a time (latency, not throughput) and reports the share that finished within
the threshold. AC-16 passes when at least 95% respond within 1 second.

    BASE_URL=... API_KEY=... uv run python -m scripts.performance
    # add --reset (and ALLOW_DESTRUCTIVE_TESTS=1) to start from an empty target

Exit code 0 = pass, 1 = fail, 2 = could not run.
"""

import argparse
import json
import random
import statistics
import time
from dataclasses import dataclass
from typing import Any

import httpx

from scripts.common import client_from_env, create_incidents, fixture_bodies, reset, run_conditions


@dataclass(frozen=True)
class Sample:
    operation: str
    status: int
    seconds: float


def build_plan(incident_ids: list[str], total: int, seed: int) -> list[tuple[str, str, Any]]:
    """The request mix: 75% GET incident, 20% POST evidence, 5% GET /health."""
    rng = random.Random(seed)  # noqa: S311 - reproducible choice of targets, not security
    evidence = fixture_bodies("evidence_valid.json")
    plan: list[tuple[str, str, Any]] = []
    for n in range(total):
        roll = n % 20
        incident_id = rng.choice(incident_ids)
        if roll < 15:
            plan.append(("GET incident", f"/incidents/{incident_id}", None))
        elif roll < 19:
            plan.append(
                ("POST evidence", f"/incidents/{incident_id}/evidence", rng.choice(evidence))
            )
        else:
            plan.append(("GET health", "/health", None))
    return plan


def run_plan(client: httpx.Client, plan: list[tuple[str, str, Any]]) -> list[Sample]:
    samples = []
    for operation, path, body in plan:
        method = "POST" if body is not None else "GET"
        started = time.perf_counter()
        try:
            status = client.request(method, path, json=body).status_code
        except httpx.HTTPError:
            status = 0  # transport failure counts as a failed request
        samples.append(Sample(operation, status, time.perf_counter() - started))
    return samples


def summarize(samples: list[Sample], threshold: float, required_share: float) -> dict[str, Any]:
    if not samples:
        raise ValueError("no samples")
    times = sorted(s.seconds for s in samples)
    errors = [s for s in samples if not 200 <= s.status < 300]
    within = sum(1 for s in samples if s.seconds <= threshold and 200 <= s.status < 300)
    share = within / len(samples)
    by_op: dict[str, list[float]] = {}
    for s in samples:
        by_op.setdefault(s.operation, []).append(s.seconds)
    return {
        "requests": len(samples),
        "errors": len(errors),
        "within_threshold": within,
        "share_within_threshold": round(share, 4),
        "threshold_seconds": threshold,
        "required_share": required_share,
        "p50_ms": round(statistics.median(times) * 1000, 1),
        "p95_ms": round(times[max(0, int(len(times) * 0.95) - 1)] * 1000, 1),
        "max_ms": round(times[-1] * 1000, 1),
        "by_operation": {
            op: {"count": len(ts), "p50_ms": round(statistics.median(ts) * 1000, 1)}
            for op, ts in sorted(by_op.items())
        },
        "passed": share >= required_share,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--incidents", type=int, default=100)
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--threshold", type=float, default=1.0, help="seconds")
    parser.add_argument("--required-share", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=30861)
    parser.add_argument("--reset", action="store_true", help="POST /reset first (destructive)")
    parser.add_argument("--json-out", help="also write the full result to this file")
    args = parser.parse_args(argv)

    with client_from_env() as client:
        if args.reset:
            reset(client)
        conditions = run_conditions(str(client.base_url))
        load_started = time.perf_counter()
        incidents = create_incidents(client, args.incidents)
        load_seconds = time.perf_counter() - load_started
        plan = build_plan([i["incidentId"] for i in incidents], args.requests, args.seed)
        summary = summarize(run_plan(client, plan), args.threshold, args.required_share)

    result = {
        "conditions": {
            **conditions,
            "incidents_loaded": args.incidents,
            "load_seconds": round(load_seconds, 2),
            "mode": "sequential, one request at a time",
            "seed": args.seed,
        },
        "summary": summary,
    }
    print(json.dumps(result, indent=2))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as out:
            json.dump(result, out, indent=2)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
