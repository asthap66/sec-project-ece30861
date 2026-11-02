# Srihari Phase 4 handoff: storage, calendar, reset

Owner: Srihari. Branch `phase4/srihari-calendar-storage`, based on Astha's
`phase4/astha-decisions` (`63e65bc`), which is based on `integration`
(`e9dd257`). Connects the two adapters Astha's `DecisionService` needs, so
`POST /incidents/{id}/decisions` and `GET /incidents/{id}/deadline-status`
no longer return 503. Models: [phase4-storage-deployment.md](../models/phase4-storage-deployment.md).

## What changed

| File | Change | Packages |
| --- | --- | --- |
| `app/holidays.py` | Versioned holiday list `us-federal-2025-2027.v1` (34 dates) | W004 |
| `app/deadline_calendar.py` | `DeadlineCalendar`: Eastern date, 4th business day, PENDING/OVERDUE/NOT_APPLICABLE and businessDays; config validation; `SHARED_CALENDAR` | W014-W018 |
| `migrations/versions/0003_decisions.py`, `app/models.py` | `decisions` and `decision_evidence` tables; composite FKs so evidence must belong to the decision's incident | W009, W010 |
| `app/services/decision_store.py` | `SQLAlchemyDecisionRepository` (Astha's protocol): row lock, append without commit, one commit, rollback on any error | W008, W011, W012 |
| `app/routes/decision_support.py` | Hooks now return the real repository (request session from `get_db`) and `SHARED_CALENDAR` | integration |
| `app/routes/system.py`, `app/routes/test_interface.py`, `app/models.py` | `/reset` and `/test/setup` truncate decisions too (`RESET_PROJECT_DATA`) | W013 |
| `tests/unit/test_deadline_calendar.py` | 30 calendar cases, expected values copied from the contract | W014-W018 |
| `tests/infrastructure/test_decision_database.py` | 15 PostgreSQL cases: round trip, no rows after 8 kinds of rejection, 409 leaves rows unchanged, NOT_MATERIAL→MATERIAL, concurrency, DB-level foreign-evidence refusal, reset/restart, migration on a Phase 3 DB | W009-W013 |
| `tests/infrastructure/test_feature_database.py` | Timestamp test compares with the database clock, not the host clock (Mohit's 4 s Docker drift failure) | clock diagnosis |
| `docs/models/*` | ER, transaction, deadline and deployment models | W058 |

## Decisions I made that the pod should confirm

1. **2025 holidays.** Model 3 lists 2026-2027 only; AC-09/AC-10 use 2025.
   I used the US federal holidays as observed (5 U.S.C. 6103) for 2025-2027.
   Every AC-09/AC-10 example needs exactly Oct 13 2025, Nov 27 2025 and
   Jan 1 2026, which this list has. One-off federal closures (days of
   mourning, executive-order days off) are not included.
2. **Dates outside 2025-2027** return 400 `DATE_OUT_OF_RANGE` instead of being
   counted against a list that doesn't cover them. A determination in 2024,
   or an `as_of` in 2028, is refused.
3. **businessDays.** PENDING: business days after the as_of date up to and
   including the due date (0 on the due date). OVERDUE: business days after
   the due date up to and including the as_of date (0 on a weekend right
   after the due date). Matches all three Model 3 examples.
   NOT_APPLICABLE: 0 (the contract only says integer).
4. **Future as_of** is allowed (Astha's service passes it through); limited by
   the supported years.
5. **incidents.status** is left as the Phase 3 column and not updated; the
   API status is always derived from the newest decision.

## Verification (2026-11-01, local, disposable PostgreSQL 16 in Docker)

| Check | Result |
| --- | --- |
| `TEST_DATABASE_URL=… uv run pytest -m "not acceptance"` | 320 passed, 0 failed |
| Same without a database | 279 passed, 41 skipped (database cases) |
| Merged with `mohit-phase4` at `4754702` (not committed): `pytest -m acceptance` against a local server on this code | **92 passed** (45 Phase 4 + 47 Phase 3), 1 skipped (HTTPS, local only) |
| Same merge, `pytest -m "not acceptance"` with database | 323 passed |
| `ruff check`, `ruff format --check`, `mypy` | Passed |

Not done here: deployment (W050/W051), restart of the deployed container
(W055), deployed latency (W056), branch-protection check (W046) and the
registry update (W060). Those follow once PRs #13, #14 and this one are merged
into `integration`.
