# Srihari Phase 5 persistence handoff — 2026-11-21

Branch `phase5/srihari-persistence`, based on `origin/integration` at `5e97de8`
(Astha's API and Mohit's Phase 5 work already merged). Implements the
persistence side of `astha-api-handoff.md`. Not deployed yet (see the end).

## What is implemented

| Piece | Where |
| --- | --- |
| `SQLAlchemyPhase5Repository` (the `Phase5Repository` protocol) | `app/services/phase5_store.py` |
| Real dependency instead of the 503 stub | `app/routes/phase5.py` `get_phase5_repository` |
| Filing-aware incident detail and Phase 4 routes (same adapter) | `app/routes/decision_support.py`, `app/services/decision_store.py` `_load` |
| `Filing` model, `Decision.corrects_decision_id` | `app/models.py` |
| Migration `0004` (upgrade and downgrade) | `migrations/versions/0004_filings_and_corrections.py` |
| Reset (`POST /reset`, `/test/setup`) also clears `filings` | `app/models.py` `RESET_PROJECT_DATA` |
| Database tests | `tests/infrastructure/test_phase5_database.py` (21) |

### Repository behavior

- `transaction(incident_id)`: one fresh transaction, `SELECT ... FOR UPDATE` on
  the incident, then a complete snapshot (evidence, newest decision, filing).
  Unknown incident is 404. Commits once after the block; any exception,
  including a failed commit, rolls back every row. Same lock as Phase 4, so
  decisions, corrections and filings on one incident serialize.
- `append_correction(data)`: inserts a **new** decision row with
  `corrects_decision_id` pointing at the replaced one, plus its evidence links.
  Nothing is updated or deleted. The newest row is the current decision, so
  incident detail and deadline-status show the correction.
- `append_filing(data, timeliness, business_days_late)`: inserts the filing
  with the timeliness and late days the service classified (stored, so a later
  holiday-list change never rewrites a recorded filing). The snapshot then has
  `filing`, and `decision_status` reports `FILED`.
- `get_timeline(incident_id)`: reads under `FOR SHARE` on the incident (waits
  for an in-progress write to commit, blocks writes while reading), so events,
  counts and duration are one consistent state. Unknown incident is 404.

### Database guarantees (not only service checks)

- `filings.incident_id` is unique: a second filing for an incident fails in
  the database, also when two requests race (tested: `[201, 409]`).
- `decisions.corrects_decision_id` is unique and a composite foreign key with
  `incident_id`: a decision is superseded at most once (history is one chain),
  and only by a decision of the same incident.
- Filing checks: `timeliness IN ('ON_TIME','LATE')`, `business_days_late >= 0`,
  non-blank accession number. Public IDs `FIL-001` are generated like
  `INC/EVD/DEC`.

### Database clock (plan item 7)

Recording times (`incidents.created_at`, `evidence/decisions/filings.recorded_at`)
now default to `clock_timestamp()` instead of `now()`. `now()` is the start of
the transaction, and a decision or filing transaction starts by waiting for the
incident lock, so a write that waited could be stamped earlier than the write it
waited behind and show up out of order in the timeline. Existing rows keep their
values. `test_sessions.created_at` is unchanged (not part of any timeline).

## Answers to Mohit's questions (provisional where the pod hasn't decided)

- **Filing fields:** stored as `filed_at` / `accession_number`, exposed as
  `filedAt` / `accessionNumber`. Model 2's `filing_date`/`filed_by` are not
  stored: the public contract has no `filedBy`. If the pod wants it, it needs a
  contract change plus a nullable column.
- **Timeline order and timestamps:** recording order. Sort key is
  `recordedAt` (database insert time, UTC), then event kind
  (incident < evidence < decision/correction < filing), then row id. User-entered
  `determinedAt`, `collectedAt`, `filedAt` are never used (tested: a correction
  that claims an earlier determination still appears after the original).
- **DECISION_RECORDED vs DECISION_CORRECTED:** a decision row with a
  `corrects_decision_id` is `DECISION_CORRECTED`; otherwise `DECISION_RECORDED`.
  Superseded decisions are visible as an earlier decision event followed by a
  correction event. No public `superseded` field was added.
- **discoveryToDeterminationDays (provisional):** exact elapsed time from
  `discoveredAt` to the **current** decision's `determinedAt`, in days, rounded
  to 2 decimals (timezone-independent). `null` when there is no decision. Needs
  pod confirmation; the code is one function,
  `discovery_to_determination_days`.
- **Calendar:** unchanged. Filing timeliness uses the shared calendar through
  `Phase5Service` (Eastern date, 4th business day after determination, approved
  holiday list). The adapter stores the result; it does no date math itself.
- **Reset:** `POST /reset` and `/test/setup` clear **all** project data,
  now including filings (REQ-14), and restart numbering. Synthetic-only isolation
  is not implemented; the plan's synthetic-only wording conflicts with REQ-14 and
  needs the pod decision Astha listed. Until then, deployed testing must use the
  agreed exclusive reset window.
- **Stale `correctsDecisionId`:** still 400 (Astha's provisional choice); the
  adapter doesn't change it.

## Migration commands

```bash
uv run alembic upgrade head      # Phase 4 (0003) -> 0004, or a fresh database -> 0004
uv run alembic downgrade 0003    # back to Phase 4: drops filings and the correction link
```

Downgrading deletes filings and correction links (the decision rows stay, as
ordinary decisions). Take a backup before downgrading a deployed database.

## Evidence (local, 2026-11-21, PostgreSQL 16 in Docker)

| Check | Result |
| --- | --- |
| `TEST_DATABASE_URL=... uv run pytest -m 'not acceptance' -q` | 361 passed, 0 skipped (includes 21 new database tests and all Phase 3/4 database tests) |
| Fresh database `alembic upgrade head` (0001 → 0004) | OK |
| Upgrade of a populated Phase 4 database, then downgrade/upgrade | OK (`test_migration_upgrades_a_populated_phase4_database`) |
| Mohit's `tests/acceptance/test_phase5_workflow.py` (branch `mohit-phase5-acceptance` 71f1b4d), over HTTP against this branch on uvicorn | **34 passed** |
| Full acceptance suite (`-m acceptance`, Phase 3/4/5) against the same server | 126 passed, 1 skipped (HTTPS check, local target) |
| Restart: create incident, evidence, decision, LATE filing; stop uvicorn; start a new process; compare | timeline byte-identical; detail still `FILED`, `LATE`, 1 business day |
| `ruff check .`, `ruff format --check .`, `mypy`, `git diff --check` | pass |

One existing test changed: Astha's
`test_phase5_routes_require_auth_and_report_missing_adapter` asserted the 503
placeholder. It is now `..._use_the_integrated_adapter`: same 401 checks, and
a valid key now reaches validation (400) instead of 503.

## Second check (edge cases, trial merge)

Ten more database tests (31 in `test_phase5_database.py`), all passing:
correction with no decision yet (400, no rows); NOT_MATERIAL corrected to
MATERIAL then filed; material correction or filing outside the calendar's
2025-2027 (400 `DATE_OUT_OF_RANGE`, no rows); LATE on the Saturday after the
deadline stored with 0 business days; two concurrent corrections of one
decision (`[201, 400]`); a correction racing a filing (one wins, state stays
consistent either way); evidence added after the filing (appears after it,
counts per category); an ordinary decision after a NOT_MATERIAL correction;
downgrade with corrections and filings present, then upgrade. The three race
tests passed 15 of 15 repeated runs.

Trial merge of `mohit-phase5-acceptance` (71f1b4d) into this branch: no
conflicts. Replaying `.github/workflows/ci.yml` on the merged tree with one
fresh database: ruff, format and mypy pass; `not acceptance` 366 passed; Phase 3
acceptance 47 passed (1 HTTPS skip); Phase 4 45 passed; Phase 5 fixtures 32
passed; **Phase 5 acceptance (blocking) 34 passed**; AC-16 restart 100/100
incidents intact; no errors in the app log.

### Found while probing (service/contract, not storage; for Astha and the pod)

- **deadline-status after filing.** An incident filed ON_TIME still reports
  `{"status": "OVERDUE", "businessDays": 10}` from
  `GET /incidents/{id}/deadline-status` once the deadline has passed, because
  `DecisionService.deadline_status` ignores the filing. The contract does not
  say what FILED incidents should report; NOT_APPLICABLE (or a filed state) is
  the likely intent. Needs a pod decision, then a small service change.
- **Filing time sanity.** A filing dated before the determination (filed
  2025-09-10, decided 2025-09-29) is accepted as ON_TIME, and a future
  `filedAt` is accepted. Astha's handoff leaves this open on purpose; the pod
  should decide whether these are 400s.

## Not done yet

- **Deployment.** Needs the reviewed integration commit. Steps: merge this
  branch and Mohit's test branch into `integration`, run the full suite, then
  build and roll out per `docs/deployment.md`. Cloud Run runs
  `alembic upgrade head` from the image's start command; record the API URL,
  tester URL, commit SHA, revision and timestamp afterwards.
- Pod decisions above (duration rule, reset scope, stale-reference status,
  `filedBy`). Each is a small, isolated change once decided.
