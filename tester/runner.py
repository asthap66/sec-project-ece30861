"""Run the acceptance suite against a target and collect results and coverage."""

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent  # repo root: tests/ lives here
SUITE = ["tests/acceptance", "-m", "acceptance"]


@dataclass
class SuiteRun:
    planned: list[str]
    records: dict[str, dict[str, Any]]
    aborted: str | None  # why the run stopped early, if it did


def run_suite(target_url: str, api_key: str, timeout_seconds: float) -> SuiteRun:
    """Run tests/acceptance against target_url, one test at a time, in order."""
    with tempfile.TemporaryDirectory() as tmp:
        results_file = Path(tmp) / "results.jsonl"
        env = {
            **os.environ,
            "BASE_URL": target_url,
            "API_KEY": api_key,
            "ALLOW_DESTRUCTIVE_TESTS": "1",  # the session was just prepared for us
            "TESTER_RESULTS_FILE": str(results_file),
        }
        command = [
            sys.executable,
            "-m",
            "pytest",
            *SUITE,
            "-p",
            "tester.pytest_plugin",
            "-q",
            "--no-header",
            "-p",
            "no:cacheprovider",
        ]
        aborted = None
        try:
            # fixed argv, no shell; the target URL goes in via the environment
            proc = subprocess.run(  # noqa: S603
                command,
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            # pytest exit codes: 0 all passed, 1 some failed; anything else means
            # pytest itself couldn't run the suite properly
            if proc.returncode not in (0, 1):
                aborted = f"the test runner exited with code {proc.returncode}"
        except subprocess.TimeoutExpired:
            aborted = f"the suite exceeded the tester's {timeout_seconds:.0f}-second run limit"

        planned: list[str] = []
        records: dict[str, dict[str, Any]] = {}
        if results_file.exists():
            for line in results_file.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                if event["event"] == "planned":
                    planned = event["tests"]
                elif event["event"] == "result":
                    records[event["nodeid"]] = event
        if not planned and aborted is None:
            aborted = "the test runner produced no test plan"
        return SuiteRun(planned=planned, records=records, aborted=aborted)


def code_coverage(
    target_url: str, api_key: str, session_id: str, timeout_seconds: float
) -> dict[str, Any]:
    """The target's code coverage for this session, from its /test/report."""

    def unavailable(why: str) -> dict[str, Any]:
        return {"covered": None, "total": None, "basis": f"Target code coverage unavailable: {why}"}

    try:
        response = httpx.get(
            f"{target_url}/test/report",
            params={"session_id": session_id},
            headers={"X-API-Key": api_key},
            timeout=timeout_seconds,
        )
    except httpx.HTTPError as exc:
        return unavailable(f"system report request failed ({type(exc).__name__})")
    if response.status_code != 200:
        return unavailable(f"system report returned HTTP {response.status_code}")
    try:
        code = response.json()["coverage"]["code"]
        covered, total, basis = code["covered"], code["total"], code["basis"]
    except (ValueError, KeyError, TypeError):
        return unavailable("system report did not include coverage.code")
    valid_counts = (covered is None and total is None) or (
        isinstance(covered, int) and isinstance(total, int) and 0 <= covered <= total
    )
    if not valid_counts or not isinstance(basis, str) or not basis:
        return unavailable("system report's coverage.code was malformed")
    return {"covered": covered, "total": total, "basis": basis}
