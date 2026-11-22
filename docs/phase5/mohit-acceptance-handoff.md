# Mohit Phase 5 acceptance handoff — 2026-11-21

Base: `origin/integration` at `5e97de8`, including Astha's API merge. This
branch prepares HTTP acceptance against the public shapes in
`astha-api-handoff.md`; it does not change production behavior or claim those
routes work. `get_phase5_repository()` still returns 503 with a valid key.

## New verification

- `tests/acceptance/test_phase5_workflow.py`: 34 collected live HTTP cases.
  Corrections cover success/current decision, retained original timeline
  event, missing/invalid/foreign evidence and unknown incident, stale
  reference, no-write observation, and filed-state conflict. Filings cover
  eligibility, before/on/after Eastern deadline, businessDaysLate, malformed
  and missing fields, duplicate conflict, stored detail and unknown incident.
  Timeline covers all five event types, IDs, UTC recording order, counts,
  corrected current decision, empty history and unknown incident. Each route
  has missing/wrong-key checks. The tests use returned IDs and independent
  fixtures, never the production calendar for expected values.
- `tests/infrastructure/test_phase5_openapi.py`: four passing offline checks
  compare the generated operation and component schemas with the handoff.
- `tests/fixtures/data/phase5_scenarios.json`: adds fixed businessDaysLate
  examples for on-time, Saturday after the deadline (LATE with zero business
  days), and Monday after the deadline (LATE with one business day).
- CI separates Phase 3, Phase 4, Phase 5 offline, and Phase 5 HTTP selections.
  The new Phase 5 HTTP selection is blocking and saves JUnit/JSONL. This branch
  should merge only when Srihari's adapter makes it pass; no broad skip, xfail
  or informational override is used.

## Executed checks

| Command | Actual result |
| --- | --- |
| `uv run pytest --collect-only -q` | 472 collected |
| `uv run pytest -m 'phase5 and acceptance' --collect-only -q` | 34 selected; collected only, not executed against a service |
| `uv run pytest -m 'phase5 and not acceptance' -q` | 11 passed |
| `uv run pytest -m 'not acceptance' -q` | 304 passed, 41 PostgreSQL skips, 127 deselected; no TEST_DATABASE_URL supplied |
| `uv run ruff check .`; `uv run ruff format --check .`; `uv run mypy`; `git diff --check` | Passed |

The 41 database skips reflect the absence of a disposable PostgreSQL service
in this focused run. The previous integrated Phase 3/4 run is recorded in
`local-validation-report.md`; it predates Astha's API merge and is not a
substitute for a new full run after Srihari's adapter. No deployed/cross-team
Phase 5 run was performed.

## Adapter handoff and contract questions

Srihari must implement the locked correction and filing transactions,
append-only history, filing-aware incident retrieval, timeline recording
timestamps/order, migration, and reset support described in Astha's handoff.
After integration, run the explicit Phase 5 HTTP selection against a
disposable local service, then all Phase 3/4 regressions, restart and reset
checks, static checks, and finally deployed and reciprocal tests in agreed
reset windows. Preserve raw JUnit/JSONL and exact deployed revisions.

The stale correction reference's 400/409 status, duplicate filing response,
supersession visibility, duration rounding, holiday policy and synthetic-only
reset requirement remain unresolved. The tests record present provisional
behavior where needed; they do not settle the shared contract.
