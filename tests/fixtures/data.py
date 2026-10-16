"""Loader for the shared synthetic JSON fixtures in tests/fixtures/data/.

Owner: Mohit. The JSON files are the pod-shareable test data (Phase 2, Q4.2),
so they stay plain JSON that the other team can use without this code.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"


@dataclass(frozen=True)
class Case:
    name: str
    body: dict[str, Any]
    expected: dict[str, Any]


def load_cases(filename: str) -> list[Case]:
    raw = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
    return [Case(c["name"], c["body"], c["expected"]) for c in raw["cases"]]


def unknown_incident_ids() -> list[str]:
    raw = json.loads((DATA_DIR / "unknown_ids.json").read_text(encoding="utf-8"))
    return list(raw["incidentIds"])


VALID_INCIDENTS = load_cases("incidents_valid.json")
INVALID_INCIDENTS = load_cases("incidents_invalid.json")
VALID_EVIDENCE = load_cases("evidence_valid.json")
INVALID_EVIDENCE = load_cases("evidence_invalid.json")
