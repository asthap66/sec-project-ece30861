# Q4 Automated validation (draft)

Lead: Mohit. Detailed results: `docs/test-results/`. Requirement mapping: `docs/test-results/traceability.md`.

## What runs, and where

| Layer | Location | Count | Needs |
| --- | --- | --- | --- |
| Unit tests (schemas, routes, repository) | `tests/unit/` | 81 | Nothing |
| Infrastructure tests (auth, errors, logging, database, migrations) | `tests/infrastructure/` | 46 | A disposable PostgreSQL for the database tests (`TEST_DATABASE_URL`) |
| Fixture checks (shared JSON cases follow the contract's field rules) | `tests/fixtures/` | 31 | Nothing |
| Script self-tests | `tests/scripts/` | 7 | Nothing |
| HTTP client self-tests | `tests/acceptance/test_client_selftest.py` | 5 | Nothing |
| **Acceptance suite** (AC-01 to AC-05, AC-14, plus `/health` and `/reset`) | `tests/acceptance/`, marker `acceptance` | 48 | `BASE_URL`, `API_KEY`. Reset tests also need `ALLOW_DESTRUCTIVE_TESTS=1` |
| **AC-16 scripts** (restart persistence, reset, response time) | `scripts/check_persistence.py`, `scripts/performance.py` | — | `BASE_URL`, `API_KEY`. The restart happens between the `create` and `verify` steps |

The acceptance suite only talks HTTP to a base URL, so the same tests run against a local app, CI, our deployment, or the other team's deployment. The shared inputs are plain JSON in `tests/fixtures/data/`.

## Continuous integration

`.github/workflows/ci.yml` runs on every push to `main` and `integration`, and on every pull request:

1. Static checks: `ruff check`, `ruff format --check`, `mypy` (strict).
2. The 170 non-acceptance tests, against a disposable PostgreSQL service.
3. Migrates and starts the app inside the job, then runs the 48 acceptance tests against it with a throwaway key.
4. AC-16 smoke test: creates 100 incidents, restarts the app, verifies them, resets, then runs the response-time check.

Latest run on `integration` (`9720693`, 2026-10-18): all green. 170 passed; acceptance 47 passed, 1 skipped (the HTTPS check skips for a local target); 100/100 persisted; 200/200 within 1 s. CI never calls a deployed service.

## Results

| Date | Target | Acceptance | Persistence | Response time |
| --- | --- | --- | --- | --- |
| 2026-10-16 | Local Docker Compose | 47 passed, 1 skipped (HTTPS) | 100/100 after app and full-stack restarts | 200/200 within 1 s, p95 16 ms (loopback) |
| 2026-10-18 | Our deployment (Cloud Run) | **48 passed**, 0 skipped | **100/100** after a revision restart; all removed by reset | **200/200 within 1 s**, p95 61 ms |

Details: [local run](../test-results/2026-10-16-local-ac16.md), [deployed run](../test-results/2026-10-18-deployed.md).

## How we know the tests catch real failures

- Against a build without the incident/evidence routes, 33 of the 35 AC-01 to AC-05 tests failed. The 2 that passed are unknown-ID 404 checks, which a missing route also satisfies.
- Before the service existed, the AC-14 tests passed against a small stub that checks keys, and failed against the bare scaffold.
- Each AC-02 / AC-05 invalid case asserts a 400 whose message names the bad field, and checks that nothing was created or attached.

## Gaps

- **AC-02 count check and AC-16 "no incidents remain"** need `GET /incidents`, which isn't in the pod contract (`docs/contract-issues.md` #2). For now we check each created ID individually.
- **Length boundaries** wait on agreed limits (`docs/contract-issues.md` #3). Our placeholders are `title` ≤ 200 and `description` ≤ 5000.
- **Phase 4 criteria** (decisions, deadlines, filing, 409 state rules) have no tests yet, because the endpoints don't exist.
- The keyed deployed run was done by Srihari using Mohit's suite. Mohit's own deployed checks so far are the keyless ones (health, HTTPS redirect, 401s).
