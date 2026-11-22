# Mohit Phase 5 acceptance handoff — 2026-11-21

Initial base: `origin/integration` at `5e97de8`, including Astha's API merge.
The branch now also contains Srihari's persistence merge `9e32887`. The HTTP
suite follows the public shapes in `astha-api-handoff.md`; the repository and
migration are described in `srihari-persistence-handoff.md`. This test branch
does not change production behavior.

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
  The new Phase 5 HTTP selection is blocking and saves JUnit/JSONL. No broad
  skip, xfail or informational override is used.

## Checks before the persistence merge

| Command | Actual result |
| --- | --- |
| `uv run pytest --collect-only -q` | 472 collected |
| `uv run pytest -m 'phase5 and acceptance' --collect-only -q` | 34 selected; collected only, not executed against a service |
| `uv run pytest -m 'phase5 and not acceptance' -q` | 11 passed |
| `uv run pytest -m 'not acceptance' -q` | 304 passed, 41 PostgreSQL skips, 127 deselected; no TEST_DATABASE_URL supplied |
| `uv run ruff check .`; `uv run ruff format --check .`; `uv run mypy`; `git diff --check` | Passed |

The 41 database skips reflect the absence of a disposable PostgreSQL service
in that focused run. The previous integrated Phase 3/4 run is recorded in
`local-validation-report.md`; it predates Astha's API merge. No deployed or
cross-team Phase 5 run was performed.

## Adapter handoff and contract questions

Srihari has implemented the locked correction and filing transactions,
append-only history, filing-aware incident retrieval, timeline recording
timestamps/order, migration, and reset support. His handoff records 34/34
Mohit HTTP cases passing in a trial merge, plus 31 database cases and an
application-process restart. Run the explicit blocking Phase 5 selection and
all Phase 3/4 regressions on the final integration CI SHA, then deployed and
reciprocal tests in agreed reset windows. Preserve raw JUnit/JSONL and exact
deployed revisions.

The stale correction reference's 400/409 status, duplicate filing response,
supersession visibility, duration rounding, holiday policy and synthetic-only
reset requirement remain unresolved. The tests record present provisional
behavior where needed; they do not settle the shared contract.

## Combined-branch verification — 2026-11-22

Merged `origin/integration` at `9e32887` into this branch without conflict.
Collection: 503 tests. `uv run ruff check .`, `uv run ruff format --check .`,
`uv run mypy`, and whitespace checks passed. Without `TEST_DATABASE_URL`,
`uv run pytest -m 'phase5 and not acceptance' -q` returned 11 passed and 31
database skips. `uv run pytest -m 'not acceptance' -q` returned 304 passed,
72 database skips, and 127 deselected. The local disposable Colima VM stalled
during startup, so a new database-backed run was not completed on this
machine; the temporary VM was removed. Srihari's passing trial and the
integration CI run at `9e32887` are separate evidence. The blocking CI run for
the final merge is still needed before release claims.
