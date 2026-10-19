# Phase 3 Gradescope answers: Q4, Q6, Q7 (paste-ready)

Owner: Mohit. Compiled 2026-10-18, 21:55 EDT (2026-10-19 01:55 UTC).

Sources: `docs/test-results/`, `docs/cross-team-testing.md`, `docs/contract-issues.md`, CI runs on GitHub, and live HTTP checks.

The exact Phase 3 rubric wording wasn't available locally. The subsections follow the team README (section 9) and the Phase 2 pod spec. Check each sentence limit against the Gradescope form before pasting.

Items marked **PENDING** or **NOT VERIFIED** are not done. Don't paste them as if they were.

## Version facts used below

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

---

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
- **Hosting:** the course overview slide says "deployed to AWS" and we're on Google Cloud. **NOT VERIFIED** whether AWS is a hard requirement.

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

---

## Q6.1 Cross-team testing in both directions

| Direction | Status | Result | Issues / owners |
| --- | --- | --- | --- |
| Our suite → their system (https://incident-clock.onrender.com) | Done 2026-10-18, about 20:25 EDT, by Mohit. Non-destructive (`ALLOW_DESTRUCTIVE_TESTS` unset), suite at `38972ff` | **45 passed, 0 failed, 3 skipped.** The skips are our 3 reset tests, left out because no reset window was agreed | None from the passing tests. Their health returns `"ok"` and ours `"OK"`; both meet `{status: string}`. Our run left synthetic incidents in their database |
| Their tester → our system | **PENDING.** Our `/test/setup` and `/test/report` are live (`f551649`). They said on 2026-10-18 around 22:00 EDT that they were running it, but no report has reached us yet | No result yet | n/a |
| Our tester → their system | Done 2026-10-18 by Srihari through our deployed tester (session `7c8dd57b-c179-48f1-8a92-465b4d8063be`). Their key is kept in our Secret Manager. This run included our 3 reset tests | **48 pass, 0 fail, 0 skipped.** Setup 201 in 0.8 s, run 200 in 9.9 s | None found |
| Our tester → our system (self-check of the interface) | Done 2026-10-18 by Srihari | 48 pass; coverage as in Q4.5 | n/a |

**Coverage available:**
- **Our tester on our system:** code 135/522 lines; component null; system 8/16 ACs exercised.
- **Our tester on their system:** code 325/406 lines (reported by their `/test/report`; their basis counts lines run at import, ours doesn't, so the two code numbers can't be compared); component null; system 8/16 ACs with at least one test run.
- **Our earlier direct suite run on their system:** no code-coverage figure (it didn't use the testing interface). It exercised AC-01 to AC-05, the REQ-07 half of AC-08, and AC-14.
- **Their tester on our system:** **PENDING.**

## Q6.2 Specification ambiguities

| Ambiguity | Effect | Resolution or proposed plan |
| --- | --- | --- |
| No instructor OpenAPI spec | Each team could build its own idea of the interface | Resolved inside our team (issue #1): build from the Phase 2 pod contract v1.0. The other team's `/openapi.yaml` is a copy of the same contract, so we line up in practice |
| AC-02 says "list all incidents" and AC-16 says "GET the incidents", but there's no list route (issue #2) | Neither team can check "count unchanged" or "no incidents remain" through the API | Proposed to the pod, not agreed: add `GET /incidents`, or reword the ACs. Until then we check per ID and use DB-level tests for "nothing saved" and "tables empty" |
| Max lengths for title/description are left open (issue #3) | Their schema only requires non-empty strings; we reject title > 200 and description > 5000. Long valid input could pass on theirs and fail on ours | Proposed: agree on numbers with the other team. Ours are placeholders, and boundary tests wait until then |
| Unknown extra fields aren't covered | One side might reject what the other accepts | We ignore them. Not yet raised with the other team |
| Error code names: only `{error, message}` is required | Tests checking exact codes could fail across teams | Our tests check the shape, not the code. We share our code list (Q3) and propose comparing |
| `/reset` and `/test/setup` clear all data on a shared deployment | One team's run can wipe the other's mid-test | No schedule was agreed. On 2026-10-18 Srihari ran our tester (resets included) against theirs, and they said they were running theirs against us. No clash has been reported. Proposed: a written schedule for Phase 4 |
| The course testing interface sits outside the pod contract | Error format for `/test/*` differs (`{message, source}`); "session" meaning is up to each team | Both teams implemented it. Ours: one active session, setup resets the data, reusing an ID gives 409 (`docs/cross-team-testing.md`) |

---

## Q7.1 Delivered and incomplete work

**Delivered:**
- Create and retrieve incidents with status `OPEN`, UTC timestamps and `INC-001` IDs (REQ-01, AC-01). Invalid input gets a 400 naming the field, and nothing is saved (REQ-02, AC-02, apart from the list-based count).
- Evidence attachment with all four categories, recorded time, unknown incident giving 404 (REQ-03, AC-03, AC-04, AC-05). Edit and delete give 405 (REQ-07).
- API-key auth on everything except `/health`, served over HTTPS (REQ-13, AC-14). `{error, message}` errors and `POST /reset` (REQ-14).
- Data persists in Cloud SQL across restarts (REQ-15, AC-16 on `f2b607c`).
- The course testing interface on our system, plus a deployed tester that runs our 48-test suite. It passed 48/48 against both our system and the other team's.
- CI that runs static checks, 212 tests, the acceptance suite and an AC-16 smoke test on every push.

**Incomplete:**
- Phase 4 decision workflow and deadlines: REQ-04, REQ-05, REQ-08, REQ-09, REQ-10; AC-06, AC-07, AC-09, AC-10, AC-15. Not started.
- Corrections, filing, timeline (REQ-06, REQ-11, REQ-12; AC-08 history half, AC-11 to AC-13). Planned for Phase 5.
- AC-16 persistence and timing on the final deployment `f551649`. Not re-run.
- Their tester's run against our system (no report yet), and cross-team AC-16 (restart and timing) in both directions.
- Pod decisions on the list route (issue #2) and length limits (issue #3).

## Q7.2 Known limitations

| ID | Affected REQ / operation | Severity | Workaround | Target phase |
| --- | --- | --- | --- | --- |
| L1 | AC-02 count check, AC-16 "no incidents remain" (no `GET /incidents`) | Medium | Per-ID 404 checks over HTTP, plus DB row-count tests in CI | Phase 4, after pod decision |
| L2 | REQ-02 length limits (`POST /incidents`) | Medium | Placeholders 200/5000; tell the other team our limits | Phase 4, after pod decision |
| L3 | AC-16 on final version `f551649` not measured | Medium | Results on `f2b607c` (same incident/evidence routes) and CI smoke runs on `f551649` | Before Phase 4 work starts |
| L4 | Their tester's report against our system not received | High for Q6 grading | Our tester passed 48/48 against them; our interface is live for theirs | Before submission if possible |
| L5 | `/test/report` coverage held in memory on one instance | Low | `max-instances 1`; restart clears coverage only, not data | Phase 4 |
| L6 | `test_feature_database.py` line 44 compares the DB clock with the host clock | Low (tests only) | Passes in CI. Failed locally once with a measured 3 to 4 s host/container clock gap | Phase 4 (Astha adds a tolerance) |
| L7 | No enforced merge or deploy gate | Medium | Team habit of merging and deploying only green commits | Phase 4 (needs branch protection, which this private repo plan doesn't offer, or a public repo) |
| L8 | `HEAD /health` gives 405 | Low | Use GET | Phase 4, if needed |
| L9 | Hosting on Google Cloud while the course slide says AWS | Unknown, **NOT VERIFIED** | Ask the instructor | Before Phase 4 |

## Q7.3 Comparison with the Phase 4 plan and changes needing pod agreement

Our Phase 2 plan (Q6.2) set Phase 4 to deliver:
- The human materiality decision workflow and state rules.
- The four-business-day deadline calculator with the holiday list.
- The deadline-status endpoint.
- Expanded fixtures, covering REQ-04, REQ-05, REQ-08, REQ-09 and REQ-10 and validated with AC-06, AC-07, AC-09, AC-10 and state-conflict tests.

That plan still holds. Phase 3 delivered what was planned (REQ-01 to REQ-03, REQ-13, and most of REQ-14/15), so Phase 4 can build on working storage, auth and deployment.

**Added to Phase 4:**
- The leftover Phase 3 items: AC-16 on the final version, the other team's report on our system, and the length-limit and list-route decisions.
- Upkeep of the course testing interface, which wasn't in the Phase 2 plan.

**Updated risks:**
- **Deadline arithmetic around holidays and Eastern Time** is still the highest-risk logic. The AC-09 and AC-10 fixtures should be written first.
- **Shared-deployment resets:** the `/test/setup` and `/reset` calls on a shared deployment can wipe the other team's runs.
- **Divergent choices on open contract points:** lengths, extra fields and error codes could make cross-team runs fail even when both systems are correct.
- **No enforced CI gate:** a bad commit could be deployed.

**Changes that need pod agreement (not decided yet):**
1. Add `GET /incidents` or reword AC-02/AC-16.
2. Exact max lengths and the whitespace policy.
3. Whether unknown fields are ignored or rejected.
4. A shared list of error codes.
5. A schedule for destructive test windows.
6. The shared holiday list for AC-10.
