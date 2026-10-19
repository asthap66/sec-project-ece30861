# Q4 Automated validation

Lead: Mohit. This draft matches `docs/submission/mohit-gradescope-ready.md`, which is the version to paste. Raw results are in `docs/test-results/`.

## Version facts

| Fact | Value | How it was checked |
| --- | --- | --- |
| Final deployed system (cover page) | `f551649` at https://incident-api-356019173418.us-central1.run.app | `X-App-Commit` header, 2026-10-19 01:55 UTC |
| Our tester | https://incident-tester-356019173418.us-central1.run.app | `GET /health` returned 200 |
| CI run on the deployed commit | [run 39182054445](https://github.com/asthap66/sec-project-ece30861/actions/runs/39182054445), `f551649`, success | GitHub Actions |
| Latest CI run on `integration` | [run 39185515218](https://github.com/asthap66/sec-project-ece30861/actions/runs/39185515218), `a520f25`, success | GitHub Actions |
| Older deployments with results | `ed5f449` (acceptance), `f2b607c` (AC-16 persistence and performance) | Q2 and `docs/test-results/2026-10-18-deployed.md` |

**Changes between `f2b607c` and `f551649`:**
- Deployment scripts and the `X-App-Commit` header.
- The `/docs` Authorize button.
- The course testing interface: `/test/setup`, `/test/report`, migration 0002 and per-session coverage via `APP_COVERAGE=1`.
- Max instances changed to 1.

The incident and evidence routes are the same, but this isn't a docs-only difference.


## Q4.1 Deployment, configuration and contract basis

Our system is deployed on Google Cloud Run with Cloud SQL PostgreSQL 16 at https://incident-api-356019173418.us-central1.run.app. It's served over HTTPS, and plain HTTP gets a 302 redirect to HTTPS. The deployed commit is `f551649`, which the service reports in the `X-App-Commit` header. On 2026-10-19 at 01:55 UTC, `/health` returned 200 without a key, and a missing or wrong key on `/incidents/INC-001` returned 401 with `{"error":"UNAUTHORIZED","message":...}`.

The test suite takes its target from two environment variables:
- `BASE_URL` must be http or https, and HTTPS is checked for non-local targets.
- `API_KEY` is sent in `X-API-Key`.

The key is never stored in the repo. Our deployed tester takes a `target_url` and only accepts approved pod URLs.

No instructor OpenAPI file was available, so both teams built from the Phase 2 pod contract v1.0 (Q5.1 to Q5.3, AC-01 to AC-16). The other team's published `/openapi.yaml` is a transcription of the same contract.

**Known deviations and open points:**
- **No `GET /incidents`:** the contract doesn't define it either, so this isn't a deviation (issue #2).
- **Length limits:** title ≤ 200 and description ≤ 5000 are our placeholders, not pod-approved values (issue #3).
- **`/test/*` errors:** these use the course testing interface's `{message, source}` format, not the project API's `{error, message}` format.
- **`HEAD /health` returns 405.** Only GET is in the contract.

## Q4.2 AC-to-test mapping and expected outputs

| AC | Tests | Success cases | Failure cases | Boundary / gaps |
| --- | --- | --- | --- | --- |
| AC-01 (REQ-01, REQ-14) | `test_ac01_create_then_retrieve_returns_identical_values[4 fixtures]`, `test_ac01_each_incident_gets_a_distinct_id` | 201, status `OPEN`, GET returns identical values; `discoveredAt` compared as the same UTC instant | n/a | Offsets −04:00, +05:30 and Z normalised to UTC; non-ASCII text |
| AC-02 (REQ-02, REQ-14) | `test_ac02_invalid_incident_is_rejected_naming_the_field[10 fixtures]` | n/a | 400, `{error, message}`, message names the field: the 3 AC-02 cases (missing description, no offset, future date 2099) plus missing title/discoveredAt/reporterName, empty title/reporterName, malformed timestamp, wrong type | Black-box tests can't count incidents (no list route). The "nothing saved" half comes from DB tests: `test_feature_database.py::test_postgres_invalid_incidents_do_not_write` (row counts stay 0 in PostgreSQL) and `tests/unit/test_incidents.py::test_missing_fields_leave_no_records` / `test_invalid_input_no_write`. Max-length cases wait on issue #3 |
| AC-03 (REQ-14) | `test_ac03_unknown_id_get_and_post_return_404[2 ids]`, `test_unknown_incident_get_is_404_with_error_format[2 ids]` | n/a | 404 with error code and message on GET and POST | IDs in both our format and a free-form string |
| AC-04 (REQ-03) | `test_ac04_three_technical_items_are_linked_to_the_incident`, `test_ac04_evidence_is_not_shared_between_incidents` | Three TECHNICAL items returned with source and timestamps; no leakage to another incident | Unknown incident gives 404 (AC-03 tests) | n/a |
| AC-05 (REQ-03) | `test_ac05_evidence_is_stored_and_returned_unchanged[6 fixtures]`, `test_invalid_evidence_is_rejected_and_not_attached[7 fixtures]` | BUSINESS_IMPACT, LEGAL, OTHER and TECHNICAL returned unchanged | 400 naming the field, and a follow-up GET shows nothing attached | Future `collectedAt` is allowed (the contract only forbids future discovery) |
| REQ-07 part of AC-08 | `test_stored_incident_cannot_be_edited_or_deleted[PUT, PATCH, DELETE]` | n/a | 405 and the incident unchanged | **Only the no-edit/no-delete half.** Correction history (REQ-06) is Phase 4/5 and has no tests |
| AC-14 (REQ-13) | `test_health_is_public`, `test_authenticated_route_rejects_bad_key[missing, wrong]`, `test_authenticated_route_accepts_valid_key`, `test_deployment_uses_https`, `test_401_uses_error_format[2]`, `test_health_body_has_status` | Health without a key, valid key accepted | 401 `{error, message}` for missing and wrong key | HTTPS check skips for local http targets |
| AC-16 (REQ-14, REQ-15) | `test_reset_requires_key[2]`, `test_reset_succeeds_and_is_repeatable` (destructive, opt-in); `scripts/check_persistence.py`; `scripts/performance.py` | Reset gives `RESET_COMPLETE`; 100/100 after restart; at least 95% of 200 requests within 1 s | Reset without a key gives 401 | "No incidents remain after reset" is only checked for the IDs we created. That doesn't prove other records are gone. The DB-level proof is `test_database.py::test_reset_clears_everything_and_restarts_ids` (tables empty) |

**Why the expected outputs are trustworthy:**
- **They come from the shared contract, not from our code.** Every expected value comes from the pod contract text, and the fixture JSON (`tests/fixtures/data/*.json`) stores its expected result next to its input.
- **The fixtures are checked.** 31 tests in `tests/fixtures/test_fixture_data.py` check that the fixtures follow the contract's field rules.
- **The tests fail when the feature is missing.** Against a build without the incident routes, 33 of 35 AC-01 to AC-05 tests failed. The 2 that passed are 404 checks, which a missing route also satisfies.
- **The suite has run against two independent implementations.** It passed against ours and against the other team's (45 passed, 3 reset tests skipped).

## Q4.3 Regression process

Every push to `main` or `integration`, and every pull request, runs `.github/workflows/ci.yml`:
1. Static checks.
2. 212 unit, infrastructure, fixture, script and tester tests against a disposable PostgreSQL 16 container.
3. The app is migrated and started inside the job, and the 48 acceptance tests run against it with a throwaway key. Reset tests are included.
4. AC-16 smoke test: create 100 incidents, restart the app, verify 100/100, reset, then the 200-request timing check.

CI never calls a deployed service. Deployed runs are recorded separately in `docs/test-results/`.

The CI run on the deployed commit `f551649` is [run 39182054445](https://github.com/asthap66/sec-project-ece30861/actions/runs/39182054445) (success):
- 212 passed.
- Acceptance: 47 passed, 1 skipped (the HTTPS check skips for a local http target).
- 100/100 incidents persisted.
- 200/200 requests within 1 s (p50 3.7 ms, p95 5.9 ms, max 8.2 ms on loopback).

The latest run on `integration`, [run 39185515218](https://github.com/asthap66/sec-project-ece30861/actions/runs/39185515218) at `a520f25`, had the same counts.

## Q4.4 Static checks and enforcement

Static checks run in the same CI job, before any tests, on every push to `main`/`integration` and on every pull request:
- `ruff check` (rules E, F, W, I, B, UP, N, S, SIM).
- `ruff format --check`.
- `mypy` in strict mode with the pydantic plugin, over `app`, `tests`, `scripts` and `tester`.

On `f551649`: ruff "All checks passed!", "85 files already formatted", mypy "Success: no issues found in 61 source files".

**Enforcement: not enforced.** Checked on 2026-10-19 with authenticated `gh api`:
- **No branch protection:** the API reports `protected: false` for both `integration` and `main`.
- **No rulesets:** the rulesets API returns 403 ("Upgrade to GitHub Pro or make this repository public"), so rulesets aren't available on this private repo.
- **No deployment gate:** the repo has no GitHub environments. Deployment is a manual `scripts/deploy_gcp.sh` run that builds any git ref and doesn't check CI status.
- **Direct pushes happen:** for example, the `infra` merges into `integration` were pushed without a PR.

CI reports failures, but a failing check doesn't block a merge or a deploy. In practice we only merged PRs and deployed commits after CI passed, and `f551649` has a passing run. That's a team habit, not a gate.

## Q4.5 Results against the final deployment

**Final cover-page version `f551649`:**

| Check | Who ran it | Result |
| --- | --- | --- |
| Full acceptance suite through our deployed tester (`/test/setup`, `/test/run`, `/test/report`), reset tests included | Srihari, using Mohit's suite (2026-10-18) | **48 pass**, 0 fail. Code coverage 135 of 522 app lines (from `/test/report`). Component coverage null (the pod spec defines no components). System coverage: 8 of 16 ACs had at least one test run (AC-01, 02, 03, 04, 05, 08, 14, 16). This doesn't mean 8 ACs are fully met: AC-08 only covers the 405 half, and AC-16 only covers reset |
| Keyless acceptance subset: `BASE_URL=<our system> uv run pytest -m acceptance`, no `API_KEY` | Mohit, 2026-10-19 01:55 UTC, suite at `a520f25` | **7 passed, 0 failed, 41 skipped** (the skipped tests need a key or are destructive). Health public, missing/wrong key gives 401 in the right format, HTTPS |
| AC-16 restart persistence and 200-request timing | n/a | **PENDING.** Not run on `f551649`. It needs the key, a Cloud Run restart and a reset, all coordinated by Srihari |

**Older deployments (not the final version):**

| Version | Check | Who | Result |
| --- | --- | --- | --- |
| `ed5f449` | `pytest -m acceptance` with `ALLOW_DESTRUCTIVE_TESTS=1` | Srihari, using Mohit's suite | 48 passed, 0 failed, 0 skipped |
| `f2b607c` | `check_persistence create`, revision restart (`incident-api-00002-msv` → `00003-ggj`), `verify`, `reset` | Srihari, using Mohit's script | 100/100 intact; reset removed all 100 created IDs |
| `f2b607c` | `scripts.performance`: 100 incidents, 200 sequential requests from a laptop | Srihari, using Mohit's script | 200/200 within 1 s; p50 48 ms, p95 61 ms, max 76 ms; 0 errors |

On the first `f2b607c` persistence attempt, one request hit the client's 10 s timeout. Cloud Run logs showed no request slower than 0.36 s, which suggests a network delay, but that wasn't confirmed. The run was repeated and passed.
