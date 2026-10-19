# mohit-answers: evidence pack for Q4, Q6 and Q7

Owner: Mohit (acceptance testing, CI, performance and persistence verification, cross-team testing).
Project: ECE 30861 Phase 3, a cybersecurity incident and evidence API for the SEC disclosure rules.
Repository: https://github.com/asthap66/sec-project-ece30861, branch `integration`.
Compiled: 2026-10-18 (US Eastern evening; 2026-10-19 UTC).

## How to use this file

**Update 2026-10-19 01:55 UTC:** `docs/submission/mohit-gradescope-ready.md` is the final, corrected version of the Q4, Q6 and Q7 answers. Where this file and that one differ, that one wins. Part 8 below embeds the current drafts, which agree with it.

This file is the evidence needed to answer three Phase 3 submission questions:

- **Q4 Automated validation**
- **Q6 Cross-team readiness**
- **Q7 Status and limitations**

It was written for a reader with no other context, such as another LLM drafting the final answers.

Rules for anyone writing answers from it:

1. **Only state what is recorded here.** Every number in this file comes from a real run, a real file in the repo, or a real HTTP response. Don't round numbers up, merge runs, or claim a run happened when it's listed as "not run".
2. **Say who ran what.** Some deployed runs used Mohit's suite but were run by Srihari, who holds the cloud credentials. This file marks each one.
3. **Keep the targets separate.**
   - Local Docker
   - CI (an app started inside the GitHub Actions job)
   - Our deployment (Google Cloud Run)
   - The other team's deployment (Render)

   They are different kinds of evidence.
4. **No secrets.** API keys are deliberately absent. Never ask for them or reconstruct them.
5. Parts 1–3 are the answer-ready summaries. Parts 4 onward are raw evidence (source files, logs, docs), included verbatim so claims can be checked.

## Contents

- Part 0: Facts at a glance
- Part 1: Q4 Automated validation (summary + evidence map)
- Part 2: Q6 Cross-team readiness (summary + evidence map)
- Part 3: Q7 Status and limitations (summary + evidence map)
- Part 4: Timeline of the work (commits and pull requests)
- Part 5: Live spot checks (raw HTTP observations)
- Part 6: Latest CI run (raw log excerpt)
- Part 7: Complete test inventory (every test ID)
- Part 8: Submission drafts as committed (final Gradescope answers, Q2, Q3)
- Part 9: Test-result records as committed
- Part 10: Contract issues and the cross-team testing interface
- Part 11: CI workflow source
- Part 12: Acceptance suite source (the test files)
- Part 13: AC-16 scripts (usage)
- Part 14: Shared fixtures (JSON)
- Part 15: The other team's published contract (`/openapi.yaml`, excerpt)

---

## Part 0: Facts at a glance

### Submission readiness (2026-10-18, about 22:15 EDT)

| Item | Status |
| --- | --- |
| Paste-ready Q4, Q6, Q7 answers | Done: `docs/submission/mohit-gradescope-ready.md` (merged via PR #11) |
| Class registry entry | Submitted (confirmed by the team) |
| Hosting on Google Cloud | Confirmed acceptable |
| Our tester → other team's system | Done: 48 pass, 0 fail, 0 skipped (Srihari) |
| Our suite → other team's system (direct) | Done: 45 passed, 0 failed, 3 skipped |
| Their tester → our system | **PENDING.** They said they were running it; no report received. Q6.1 says pending |
| AC-16 restart and timing on final `f551649` | **PENDING.** Not run; Q4.5 shows the earlier `f2b607c` results separately |

Both pending items are disclosed honestly in the answers, so they don't block submitting. If either result arrives first, Q4.5 or Q6.1 should be updated with the real numbers.

### Team

| Person | Role | Branch |
| --- | --- | --- |
| Srihari | Infrastructure, database, auth, deployment, course testing interface, tester service | `infra` |
| Astha | Incident and evidence endpoints | `feature/incident-evidence-api` |
| Mohit | Acceptance suite, fixtures, CI, AC-16 scripts, test-result records, cross-team coordination; leads Q4 and Q6, consolidates Q7 | `acceptance-ci` |

All work merges into `integration`. `main` was frozen at `d2198a4` on 2026-10-16 by team decision.

### Services

| Thing | URL | Notes |
| --- | --- | --- |
| Our system | https://incident-api-356019173418.us-central1.run.app | Google Cloud Run + Cloud SQL PostgreSQL 16, HTTPS, `X-App-Commit` header shows the deployed commit (`f551649` at compile time; this is the final version) |
| Our tester | https://incident-tester-356019173418.us-central1.run.app | Course testing interface: `POST /test/setup`, `POST /test/run`, `GET /test/report`. Runs our acceptance suite |
| Other team's system | https://incident-clock.onrender.com | Publishes its contract at `/openapi.yaml` |
| Other team's tester | https://incident-clock-tester.onrender.com | Course testing interface |

### Specification

- No instructor OpenAPI file was found. The team agreed on 2026-10-16 to build from the **Phase 2 pod contract v1.0** (Phase 2 - Pod.pdf, Q5.1–Q5.3, AC-01 to AC-16). The decision is recorded in `docs/contract-issues.md` #1.
- The other team's `/openapi.yaml` describes itself as a "machine-readable transcription of the pod's Phase 2 common interface contract (… specification v1.0)", so both teams built from the same source (Part 15).
- The course separately defines a "Cross-team Testing Interface" (`/test/setup`, `/test/report` on systems; `/test/setup`, `/test/run`, `/test/report` on testers). Srihari implemented both sides on 2026-10-18 (Part 10).

### Headline numbers

| Evidence | Target | Who ran it | Result |
| --- | --- | --- | --- |
| Acceptance suite | Earlier deployment `ed5f449` | Srihari, using Mohit's suite | **48 passed, 0 failed, 0 skipped** |
| Acceptance suite via our tester | Our deployment (`f551649`) | Srihari, through the deployed tester | **48 pass**; code coverage 135/522 lines; 8/16 ACs had at least one test run (not 8 fully met) |
| Keyless acceptance subset | Final deployment `f551649` | Mohit, 2026-10-19 01:55 UTC | **7 passed, 0 failed, 41 skipped** (no key available to Mohit) |
| AC-16 persistence and timing | Final deployment `f551649` | n/a | **Not run** (needs the key, a restart and a reset, all coordinated by Srihari) |
| Our tester → other team's system | Their deployment | Srihari, 2026-10-18 | **48 pass, 0 fail, 0 skipped**; code 325/406 (their basis); system 8/16 |
| Restart persistence (AC-16) | Earlier deployment `f2b607c` (same incident/evidence routes; not the final version) | Srihari, using Mohit's script | **100/100 incidents intact** after a Cloud Run revision restart; all removed by reset |
| Response time (AC-16) | Earlier deployment `f2b607c` | Srihari, using Mohit's script | **200/200 within 1 s** (target 95%); p50 48 ms, p95 61 ms, max 76 ms; 0 errors |
| Acceptance suite, non-destructive | **Other team's** deployment | Mohit | **45 passed, 0 failed, 3 skipped** (the 3 `/reset` tests, skipped on purpose) |
| Acceptance suite | Local Docker Compose (`f6b8df6`) | Mohit | 47 passed, 1 skipped (HTTPS check skips locally) |
| Restart persistence | Local Docker Compose | Mohit | 100/100 after an app restart **and** after a full stack restart |
| Response time | Local Docker Compose | Mohit | 200/200 within 1 s; p50 6.4 ms, p95 16.1 ms, max 31.4 ms (loopback) |
| CI, latest | `integration` at `c4b6643` | GitHub Actions | ruff, format, mypy clean; 212 passed; acceptance 47 passed + 1 skipped; 100/100 persisted; 200/200 within 1 s |
| Test inventory | Repo | — | 260 tests collected: 81 unit, 63 infrastructure, 31 fixture checks, 7 script self-tests, 25 tester tests, 53 in `tests/acceptance` (48 marked `acceptance` + 5 client self-tests) |

---

## Part 1: Q4 Automated validation

### 1.1 What Q4 asks for (from the project README, section 9)

> Q4 Automated validation | Mohit | Test mappings, CI/static checks, deployed run results, failure explanations

### 1.2 Answer-ready summary

**Layers of automated validation.** Counts come from `pytest --collect-only` on `integration`; see Part 7.

| Layer | Location | Tests | Needs |
| --- | --- | --- | --- |
| Static checks | `ruff check`, `ruff format --check`, `mypy --strict` (pydantic plugin) over `app`, `tests`, `scripts` | — | Nothing |
| Unit tests: schemas, incident/evidence routes, repository | `tests/unit/` | 81 | Nothing |
| Infrastructure tests: auth, errors, logging, database, migrations, course testing interface | `tests/infrastructure/` | 63 | Database tests need a disposable PostgreSQL in `TEST_DATABASE_URL`; otherwise they skip |
| Fixture checks: every shared JSON case obeys the contract's field rules | `tests/fixtures/` | 31 | Nothing |
| AC-16 script self-tests | `tests/scripts/` | 7 | Nothing |
| Tester service tests (Srihari) | `tests/tester/` | 25 | Nothing |
| HTTP client self-tests | `tests/acceptance/test_client_selftest.py` | 5 | Nothing |
| **Acceptance suite**, black-box over HTTP | `tests/acceptance/`, marker `acceptance` | 48 | `BASE_URL`, `API_KEY`; `/reset` tests also need `ALLOW_DESTRUCTIVE_TESTS=1` |
| **AC-16 scripts**: restart persistence, reset, response time | `scripts/check_persistence.py`, `scripts/performance.py` | — | `BASE_URL`, `API_KEY`; the restart happens between `create` and `verify` |

**Design of the acceptance suite (Mohit).**
- It only speaks HTTP to `BASE_URL` with the `X-API-Key` header. That way the identical suite runs against a local app, the CI app, our deployment, the other team's deployment, or behind our tester service.
- Test data lives in shared JSON fixtures (`tests/fixtures/data/*.json`). Each case has the form `{name, body, expected}` and is written in the contract's camelCase field format. The other team can reuse them.
- Tests that reset data are opt-in (`ALLOW_DESTRUCTIVE_TESTS=1`), so pointing the suite at someone else's system never wipes it by accident.
- Assertions are behavioural:
  - Created values come back unchanged (timestamps as the same UTC instant).
  - Invalid input gets a 400 whose `message` names the offending field, and nothing is created or attached.
  - Unknown IDs get a 404.
  - PUT, PATCH and DELETE get a 405.
  - A missing or wrong key gets a 401.
  - Every error body has `{error, message}`.
  - HTTPS is used for non-local targets.

**Requirement-to-test mapping.** Full table in Part 9, `traceability.md`.

| Criterion | Tests |
| --- | --- |
| AC-01 create and retrieve with identical values; distinct IDs | `test_ac01_05_incidents_evidence.py::test_ac01_*` |
| AC-02 invalid incidents give 400 naming the field (10 fixture cases) | `test_ac02_invalid_incident_is_rejected_naming_the_field[*]` |
| AC-03 unknown incident ID gives 404 on GET and on evidence POST | `test_ac03_*`, `test_system_endpoints.py::test_unknown_incident_get_is_404_with_error_format` |
| AC-04 three TECHNICAL evidence items linked; isolation between incidents | `test_ac04_*` |
| AC-05 every valid evidence item returned unchanged; invalid evidence gives 400 and isn't attached | `test_ac05_*` |
| REQ-07 edit and delete give 405 | `test_edit_and_delete_are_rejected_with_405[*]` |
| AC-14 health is public; missing or wrong key gives 401; valid key accepted; HTTPS | `test_ac14_security.py` |
| AC-14 / REQ-14 error format | `test_system_endpoints.py::test_401_uses_error_format` |
| AC-16 reset returns `RESET_COMPLETE`, needs a key, is repeatable | `test_system_endpoints.py::test_reset_*` (destructive) |
| AC-16 restart persistence; reset (per created ID) | `scripts/check_persistence.py create / verify / reset` |
| AC-16 response time: 95% within 1 s at 100 incidents | `scripts/performance.py` (200 requests: 75% GET incident, 20% POST evidence, 5% health; seed 30861) |

**Continuous integration.** File `.github/workflows/ci.yml`, in Part 11. It runs on every push to `main` and `integration` and on every pull request:
1. `uv sync --locked`, `ruff check`, `ruff format --check`, `mypy`.
2. All non-acceptance tests against a disposable PostgreSQL 16 service container.
3. `alembic upgrade head`, start the app inside the job, then run the 48 acceptance tests against it with a throwaway key and `ALLOW_DESTRUCTIVE_TESTS=1`.
4. AC-16 smoke test: create 100 incidents, kill and restart the app, verify 100/100, reset, then the response-time check.
5. Print the app log; stop the app.

CI never calls a deployed service. The latest run is `integration` at `c4b6643`, run 39184911384, 57 s, success. Raw lines are in Part 6:
- ruff: "All checks passed!"; format: "87 files already formatted"; mypy: "Success: no issues found in 61 source files".
- 212 passed (non-acceptance).
- Acceptance: 47 passed, 1 skipped (the HTTPS check skips for a local http target).
- "verified 100/100 incidents intact".
- Response time: 200/200 within 1 s, 0 errors, max 18.0 ms (loopback inside the runner).

**Recorded runs.** These are the results tables.

| Date | Target | Acceptance | Persistence | Response time | Ran by |
| --- | --- | --- | --- | --- | --- |
| 2026-10-16 | Local Docker Compose (`f6b8df6`) | 47 passed, 1 skipped (HTTPS, local) | 100/100 after app restart; 100/100 after full stack restart; reset left 100/100 returning 404 | 200/200 ≤ 1 s; p50 6.4 ms, p95 16.1 ms, max 31.4 ms | Mohit |
| 2026-10-18 | Our deployment (`ed5f449`) | **48 passed**, 0 skipped | — | — | Srihari, Mohit's suite |
| 2026-10-18 | Earlier deployment `f2b607c` | — | **100/100** after revision `incident-api-00002-msv` → `incident-api-00003-ggj`; reset removed all 100 | **200/200 ≤ 1 s**; p50 48 ms, p95 61 ms, max 76 ms; 0 errors | Srihari, Mohit's scripts |
| 2026-10-18 | Our deployment (`f551649`) via our tester | **48 pass**; code coverage 135/522 lines; 8/16 ACs (AC-01, 02, 03, 04, 05, 08, 14, 16) | — | — | Srihari |
| 2026-10-18 | Other team's deployment | **45 passed, 0 failed, 3 skipped** (reset tests, on purpose) | not run | not run | Mohit |

**Evidence that the tests detect real failures.** This is the "failure explanations" part of Q4.
- **Mutation-style check.** Against a build of the app *without* Astha's incident and evidence routes, 33 of the 35 AC-01 to AC-05 tests failed. The 2 that still passed are unknown-ID 404 checks, which a missing route also satisfies by returning 404.
- **AC-14 checks.** Before the real service existed, the AC-14 tests passed against a throwaway local stub that checked keys, and failed against the bare scaffold that had no routes.
- **Real failures seen and explained.**
  1. *CI failure on PR #6.* The setup-uv post-job cache prune timed out because a background `uv run uvicorn` held the uv cache lock. The fix launches the app with `.venv/bin/uvicorn` and adds an always-run "Stop app" step. The next run passed.
  2. *Local failure of `tests/infrastructure/test_feature_database.py::test_postgres_create_retrieve_evidence_restart_reset`* (Astha's test, line 44: `assert before <= recorded <= datetime.now(UTC)`). The suspected cause is clock skew, not confirmed: the Docker Desktop VM's clock (which sets PostgreSQL `now()`) differed from the host clock by about 3–4 s (host `date -u` 21:10:30 vs container 21:10:27; the assertion showed DB 21:10:21 vs host 21:10:17). It passes in CI. The fix is a small tolerance.
  3. *One client-side timeout* (10 s) during the first deployed persistence run. Cloud Run's request logs showed no request slower than 0.36 s, which suggests a network delay; that wasn't confirmed. The run was repeated and passed.
  4. *Static-check failures during development*, all fixed before merge: a mypy `no-any-return` in `assertions.py`, Ruff E501 long lines in the scripts, and a Ruff import-order issue in `conftest.py`.

**Gaps (honest limits of the validation).**
- AC-02's count check and AC-16's "no incidents remain" need a list route (`GET /incidents`), which the pod contract doesn't have (contract issue #2). Over HTTP, both are only checked for the IDs we created. DB-level tests (`test_postgres_invalid_incidents_do_not_write`, `test_reset_clears_everything_and_restarts_ids`) cover the rest in CI.
- Length-boundary tests wait on agreed limits (issue #3). The placeholders are title ≤ 200, description ≤ 5000.
- There are no tests for the Phase 4 operations (decisions, corrections, deadline status, filing, timeline) or the 409 state rules, because those operations don't exist yet.
- Mohit's own keyed runs against our deployment were done by Srihari, who holds the key in Secret Manager. Mohit's personal checks of our deployment are keyless (Part 5).
- Response times are from one laptop at one time of day.

### 1.3 Evidence map for Q4

| Claim | Where |
| --- | --- |
| Test counts per layer | Part 7 |
| CI steps | Part 11 |
| Latest CI output | Part 6 |
| Deployed results | Part 9, `2026-10-18-deployed.md`; Part 8, Q2; Part 10, `cross-team-testing.md` "Live check" |
| Local results | Part 9, `2026-10-16-local-ac16.md` |
| Traceability | Part 9, `traceability.md` |
| Suite design | Parts 12 to 14 (the HTTP client and scripts are in the repo) |

---

## Part 2: Q6 Cross-team readiness

### 2.1 What Q6 asks for (README section 9)

> Q6 Cross-team readiness | Mohit | Both testing directions, specification ambiguities, pod decisions

Grading note from the course overview slides: assessment includes "pod cross-testing, which involves evaluating the quality and effectiveness of tests on both one's own and others' systems."

### 2.2 Answer-ready summary

**Shared basis.**
- Both teams built from the Phase 2 pod contract v1.0.
- The other team's `/openapi.yaml` (Part 15) lists exactly the operations and fields in our contract: `GET /health`, `POST /incidents`, `GET /incidents/{id}`, `POST /incidents/{id}/evidence`, `POST /reset`, plus the Phase 4 operations.
- Neither file includes `GET /incidents`.
- The course testing interface is separate from the pod contract, and both teams have implemented it.

**Testing directions.**

| Direction | What happened | Result |
| --- | --- | --- |
| Our suite → their system (`incident-clock.onrender.com`) | 2026-10-18, about 8:30 PM US Eastern, run by Mohit from a laptop, without `ALLOW_DESTRUCTIVE_TESTS`, with their key (shared privately) | **45 passed, 0 failed, 3 skipped.** Skips are the `/reset` tests in `test_system_endpoints.py`, skipped on purpose. All AC-01 to AC-05, REQ-07 and AC-14 tests passed, including HTTPS |
| Their tester → our system | Our system has the course interface (`/test/setup`, `/test/report`, Srihari, `f551649`). We sent our system and tester URLs; Srihari sends the key privately | **Pending.** They said around 22:00 EDT that they were running it; no report received |
| Our tester → their system | Done 2026-10-18 by Srihari, session `7c8dd57b-c179-48f1-8a92-465b4d8063be` | **48 pass, 0 fail, 0 skipped**; code 325/406 (their basis); system 8/16 |
| Our tester → our system (check of our own interface) | 2026-10-18, Srihari | 48 pass; code coverage 135/522 lines; component coverage null (pod spec defines no components); system coverage 8/16 ACs |

**What the 45 passes (3 skipped) show.** The other team's AC-01 to AC-05, REQ-07 and AC-14 behaviour matches the contract as our tests read it. It says nothing about their AC-16 behaviour (persistence, reset, response time), which we haven't run against them.

**Observed differences between the two systems.** These are real HTTP responses, from Part 5 and the run record.
- Health body: ours `{"status":"OK"}`, theirs `{"status":"ok"}`. Both satisfy `{status: string}`.
- 401 message: ours "missing or invalid API key", theirs "missing or invalid X-API-Key header". Both use `{error: "UNAUTHORIZED", message}`.
- `/test/*` errors on both sides use `{message, source: "system"}`. Theirs gave `INVALID_SESSION_ID` when `session_id` was missing.

**Specification ambiguities and pod decisions.**

| Topic | Contract | Ours | Theirs | Status |
| --- | --- | --- | --- | --- |
| Which spec | No instructor OpenAPI found | Phase 2 pod contract v1.0 | Same (their `/openapi.yaml`) | **Decided** (issue #1) |
| Check order (auth vs 404 vs validation) | Model 4 in the pod spec | Auth → method → existence → body → state | Not stated | **Resolved by spec** (issue #4) |
| `GET /incidents` | Not defined, yet AC-02 says "list all incidents" and AC-16 says "GET the incidents" | Not implemented (405) | Not in their spec | Proposal written (issue #2). Both omit it, so the systems agree. Checked per ID instead |
| Max lengths for title/description | Not specified | 200 / 5000 (placeholders in `app/config.py`) | `minLength: 1` only; "Max length agreed by both teams (open)" | **Open** (issue #3). Risk: longer valid input is accepted by them and rejected by us with a 400 |
| Unknown extra fields | Not specified | Ignored | Not specified | Unconfirmed; no failures seen |
| Error code names | Only `{error, message}` | `UNAUTHORIZED`, `NOT_FOUND`, `METHOD_NOT_ALLOWED`, `INTERNAL_ERROR`, `INVALID_<FIELD>`, `INVALID_BODY` | `UNAUTHORIZED`, `NOT_FOUND` observed | Our tests check shape, not exact codes |
| Reset coordination | `/reset` and `/test/setup` clear all data | One active session; a new setup resets | Same interface | **Open:** no agreed time window, so destructive runs weren't done cross-team |

**Readiness offered to the other team.**
- System URL plus HTTPS.
- Tester URL.
- A test key over a private channel only, never in git, chat screenshots or the report.
- Shared JSON fixtures.
- `tests/acceptance/` runnable with `uv run pytest -m acceptance`.
- Our silent-contract choices are documented in Q3.

### 2.3 Evidence map for Q6

| Claim | Where |
| --- | --- |
| Our run on their system | Part 9, `2026-10-18-cross-team-ours-on-theirs.md` |
| Checklist and status | Part 9, `cross-team.md` |
| Testing interface on our side | Part 10, `cross-team-testing.md` |
| Their contract | Part 15 |
| Ambiguities | Part 10, `contract-issues.md`; Part 8, Q3 "Our choices where the contract is silent" |
| Live differences | Part 5 |

---

## Part 3: Q7 Status and limitations

### 3.1 What Q7 asks for (README section 9)

> Q7 Status and limitations | All; Mohit consolidates | Changes, unfinished scope, defects, Phase 4 adjustments

### 3.2 Answer-ready summary

**Status at submission (2026-10-18).**
- **Delivered (Phase 3 scope):**
  - Every Phase 3 contract operation: `GET /health` (public), `POST /incidents`, `GET /incidents/{incidentId}`, `POST /incidents/{incidentId}/evidence`, `POST /reset`.
  - PostgreSQL storage with Alembic migrations.
  - `X-API-Key` auth on everything except `/health`, compared in constant time.
  - `{error, message}` errors, with 400s that name the bad field.
  - 404 for unknown IDs, 405 for edit and delete.
  - Request timestamps with an offset, returned as UTC.
  - `INC-001` / `EVD-001` IDs that restart after reset.
  - Request logging without headers or bodies.
- **Course testing interface:** the system has `POST /test/setup` and `GET /test/report` with per-session code coverage. A separate tester service has `POST /test/setup`, `POST /test/run` and `GET /test/report`.
- **Deployed:**
  - Google Cloud Run (us-central1) plus Cloud SQL PostgreSQL 16, over HTTPS (`http://` gets a 302 to `https://`).
  - Secrets live in Secret Manager.
  - The commit is in the `X-App-Commit` header.
  - One warm instance (max instances 1, for coverage consistency).
- **Validated:** see Part 1. 48/48 deployed, 100/100 persisted, 200/200 under 1 s, CI green.
- **Cross-team:** 45 passed, 0 failed, 3 skipped of our suite on their system. Our tester against them: 48 pass, 0 fail (Srihari). Their tester against us: pending.

**Changes from the Phase 2 plan.**
- **Specification source:** the Phase 2 pod contract v1.0, because no instructor OpenAPI file was available (issue #1).
- **Hosting:** Google Cloud Run and Cloud SQL (confirmed acceptable for the course, 2026-10-18).
- **Auth-first precedence:** the API key is checked before routing, validation or lookup (issue #4, matching Model 4).
- **AC-16 as scripts, not pytest tests:** a restart has to happen between steps.
- **Course testing interface added**, which wasn't in the Phase 2 pod contract: system `/test/*` endpoints and a deployed tester. The new `test_sessions` table comes in migration 0002.

**Unfinished scope.**
- Phase 4 operations: decisions, corrections, deadline status, filing, timeline. 409 state rules aren't exercised.
- `GET /incidents` isn't in the contract (issue #2).
- Length limits are placeholders (issue #3), so there are no boundary tests.
- Their tester's report against our system hasn't arrived, and cross-team AC-16 (restart and timing) hasn't been done in either direction.
- Component coverage in tester reports is null, because the pod spec defines no component list.
- The class registry entry is submitted (confirmed by the team, 2026-10-18).

**Known defects and risks.**
- **Clock-sensitive database test** (`test_feature_database.py` line 44) fails when the DB clock and the test host's clock disagree by a few seconds. Owner: Astha. Fix: add a tolerance.
- **One deployed-run client timeout**, attributed to the network and not reproduced.
- **Coverage measurements are in memory on one instance.** A restart clears them. Concurrent `/test/*` and project requests could misattribute lines (documented in `app/coverage_runtime.py`).
- **`HEAD /health` returns 405.** It isn't a contract operation, but some uptime checkers use HEAD.
- **Our cross-team run left synthetic incidents** in the other team's database.
- **Persistence and performance numbers** come from deployment `f2b607c`, while the acceptance numbers are from `ed5f449` and `f551649`. The API is the same, but the commits differ, and that should be stated.

**Adjustments for Phase 4.**
1. Run both teams' testers against each other's systems; record failures and who owns each.
2. Settle issues #2 and #3 with the other team; add length-boundary tests and, if agreed, a list-count check.
3. Implement the Phase 4 operations. Extend fixtures and the acceptance suite with their ACs, including 409 state rules and the `as_of` deadline checks.
4. Agree a reset window; run destructive tests and AC-16 in both directions.
5. Add a timestamp tolerance to the clock-sensitive test.

### 3.3 Evidence map for Q7

| Claim | Where |
| --- | --- |
| Operation status | Part 8, Q3 |
| Deployment facts | Part 8, Q2 |
| Limitations as drafted | Part 8, Q7 |
| Interface details | Part 10 |
| Defects | Part 1.2 "Real failures seen and explained" |

---

## Part 4: Timeline of the work

### 4.1 Pull requests

| PR | Title | From → into | Author | Merged (UTC) |
| --- | --- | --- | --- | --- |
| #1 | test: add acceptance HTTP client, AC-14 security tests, and traceability table | acceptance-ci → main | Mohit | 2026-10-16 20:02 |
| #2 | docs: record contract evidence for GET /incidents gap and error format | acceptance-ci → main | Mohit | 2026-10-16 20:04 |
| #3 | test: add shared JSON fixtures and system endpoint acceptance tests | acceptance-ci → integration | Mohit | 2026-10-16 21:55 |
| #4 | Feature/incident evidence api | feature/incident-evidence-api → integration | Astha | 2026-10-17 01:58 |
| #5 | test: AC-01 to AC-05 acceptance tests and spec decision | acceptance-ci → integration | Mohit | 2026-10-17 01:59 |
| #6 | test: AC-16 performance and persistence scripts, local run results | acceptance-ci → integration | Mohit | 2026-10-17 02:13 |
| #7 | docs: deployed run results, Q4 and Q6 drafts | acceptance-ci → integration | Mohit | 2026-10-18 22:53 |
| #8 | docs: cross-team run, our suite against incident-clock | acceptance-ci → integration | Mohit | 2026-10-19 00:26 |
| #9 | docs: Q6 cross-team readiness and Q7 status and limitations | acceptance-ci → integration | Mohit | 2026-10-19 01:20 |

Srihari's infrastructure, deployment and testing-interface work was merged from `infra` into `integration` directly; see the commit log below.

### 4.2 Commit log of `integration` (oldest first)

```
e0f54e4 2026-10-16 Mohit  chore: initialize Phase 3 project scaffold
2ebc101 2026-10-16 Mohit  test: add acceptance HTTP client, AC-14 security tests, and traceability table
bfdb08d 2026-10-16 Mohit Manna  Merge pull request #1 from asthap66/acceptance-ci
bbc81d3 2026-10-16 Mohit  docs: record contract evidence for GET /incidents gap and error format
d2198a4 2026-10-16 Mohit Manna  Merge pull request #2 from asthap66/acceptance-ci
4887b57 2026-10-16 Srihari  Add infrastructure: config, database, models, migration, auth, errors, health and reset
f592bca 2026-10-16 Srihari  Merge infra into integration
632dc9e 2026-10-16 Mohit  ci: run database and acceptance tests against disposable PostgreSQL
e98e158 2026-10-16 asthap66  Implement Phase 3 incident and evidence API
dadf112 2026-10-16 Mohit  test: add shared JSON fixtures and system endpoint acceptance tests
1c61127 2026-10-16 Mohit Manna  Merge pull request #3 from asthap66/acceptance-ci
ba86973 2026-10-16 asthap66  Merge origin/integration and reconcile contract requirements
886a37f 2026-10-16 asthap66  Integrate incident and evidence API with PostgreSQL infrastructure
ee0ed79 2026-10-16 Mohit  test: add AC-01 to AC-05 acceptance tests driven by shared fixtures
63c10f9 2026-10-16 Mohit Manna  Merge pull request #4 from asthap66/feature/incident-evidence-api
3e5d5ab 2026-10-16 Mohit  Merge remote-tracking branch 'origin/integration' into acceptance-ci
654e0bf 2026-10-16 Mohit  docs: record team decision to build against the Phase 2 pod spec
f6b8df6 2026-10-16 Mohit Manna  Merge pull request #5 from asthap66/acceptance-ci
bf25286 2026-10-16 Mohit  test: add AC-16 performance and persistence scripts, record local run
8c7d6ca 2026-10-16 Mohit  ci: run the in-job app without uv run so cache cleanup isn't blocked
3ff30e9 2026-10-16 Mohit Manna  Merge pull request #6 from asthap66/acceptance-ci
f1b00cc 2026-10-17 Srihari  Add Q2/Q3 submission drafts and an X-App-Commit header
e23a57c 2026-10-17 Srihari  Merge infra into integration (Q2/Q3 drafts, X-App-Commit header)
85f6416 2026-10-17 Srihari  Clean validation messages; update Q3 now the incident routes exist
f2b607c 2026-10-17 Srihari  Merge infra into integration (validation messages, Q3 update)
8900e4e 2026-10-18 Srihari  Deploy to Google Cloud Run over HTTPS; fill in Q2 and update Q3
baee001 2026-10-18 Srihari  Merge infra into integration (deployment, Q2/Q3)
1303c62 2026-10-18 Srihari  Add an Authorize button for X-API-Key on /docs
ed5f449 2026-10-18 Srihari  Merge infra into integration (docs Authorize button)
67b5df4 2026-10-18 Srihari  Q2: record the redeployed commit (ed5f449)
9720693 2026-10-18 Srihari  Merge infra into integration (Q2 commit update)
d4b0e10 2026-10-18 Mohit  docs: record the deployed run and draft Q4 and Q6
38972ff 2026-10-18 Mohit Manna  Merge pull request #7 from asthap66/acceptance-ci
61be11e 2026-10-18 Mohit  docs: record our suite's run against the other team's service
d412738 2026-10-18 Mohit Manna  Merge pull request #8 from asthap66/acceptance-ci
6d88509 2026-10-18 Srihari  Add the course testing interface on the system: POST /test/setup, GET /test/report
f551649 2026-10-18 Srihari Srikanth  Add the tester service for the course testing interface
c7b3a0b 2026-10-18 Srihari Srikanth  Document the cross-team testing interface and the deployed tester
16f6764 2026-10-18 Mohit  docs: finish Q6 and draft Q7
c4b6643 2026-10-18 Mohit Manna  Merge pull request #9 from asthap66/acceptance-ci
569bbb3 2026-10-18 Mohit  docs: add mohit-answers evidence pack; update Q4/Q6/Q7 for the testing interface
a520f25 2026-10-18 Mohit Manna  Merge pull request #10 from asthap66/acceptance-ci
937c44a 2026-10-18 Mohit  docs: final Q4/Q6/Q7 answers, f551649 results, and corrected stale claims
50992d1 2026-10-18 Srihari Srikanth  Record the cross-team run against the other team's system
306b55a 2026-10-18 Srihari Srikanth  Merge remote-tracking branch 'origin/integration' into integration
18e79c3 2026-10-18 Mohit  Merge remote-tracking branch 'origin/integration' into acceptance-ci
4179bc5 2026-10-18 Mohit  docs: record our tester's 48/48 run against the other team; update Q6/Q7
```

## Part 5: Live spot checks (raw HTTP observations)

Captured by Mohit with `curl` on 2026-10-19 around 01:24 UTC, without any API key.

```text
Mon Oct 19 01:24:18 UTC 2026
GET https://incident-api-356019173418.us-central1.run.app/health -> {"status":"OK"} 200
x-app-commit: f551649
GET http://…/health -> 302 https://incident-api-356019173418.us-central1.run.app/health
GET https://incident-api-356019173418.us-central1.run.app/incidents/INC-001 (no key) -> {"error":"UNAUTHORIZED","message":"missing or invalid API key"} 401
GET https://incident-api-356019173418.us-central1.run.app/incidents/INC-001 (wrong key) -> {"error":"UNAUTHORIZED","message":"missing or invalid API key"} 401
POST https://incident-api-356019173418.us-central1.run.app/test/setup (no key) -> {"error":"UNAUTHORIZED","message":"missing or invalid API key","source":"system"} 401
GET tester /health -> {"status":"OK"} 200
GET https://incident-clock.onrender.com/health -> {"status":"ok"} 200
GET https://incident-clock.onrender.com/incidents/INC-001 (no key) -> {"error":"UNAUTHORIZED","message":"missing or invalid X-API-Key header"} 401
```

## Part 6: CI run excerpt

GitHub Actions run 39184911384 on `integration` at `c4b6643`, success. The run on the deployed commit `f551649` (39182054445) and run 39185515218 (`a520f25`) have the same counts. Lines are `step | output`.

```text
Ruff lint | All checks passed!
Ruff format check | 87 files already formatted
mypy | Success: no issues found in 61 source files
pytest (unit, infrastructure, client self-tests) | ================ 212 passed, 48 deselected, 1 warning in 6.76s =================
Start app for acceptance tests | {"status":"OK"}
pytest (acceptance, local app) | =========== 47 passed, 1 skipped, 212 deselected, 1 warning in 0.88s ===========
AC-16 persistence across an app restart | created 100 incidents; state saved to ci-run.json
AC-16 persistence across an app restart | verified 100/100 incidents intact
AC-16 response time | {
AC-16 response time |   "conditions": {
AC-16 response time |     "date": "2026-10-19T01:21:22Z",
AC-16 response time |     "target": "http://127.0.0.1:8000",
AC-16 response time |     "client_commit": "c4b6643",
AC-16 response time |     "client_host": "Linux x86_64, Python 3.12.12",
AC-16 response time |     "incidents_loaded": 100,
AC-16 response time |     "load_seconds": 0.28,
AC-16 response time |     "mode": "sequential, one request at a time",
AC-16 response time |     "seed": 30861
AC-16 response time |   "summary": {
AC-16 response time |     "requests": 200,
AC-16 response time |     "errors": 0,
AC-16 response time |     "within_threshold": 200,
AC-16 response time |     "share_within_threshold": 1.0,
AC-16 response time |     "threshold_seconds": 1.0,
AC-16 response time |     "required_share": 0.95,
AC-16 response time |     "max_ms": 18.0,
AC-16 response time |     "by_operation": {
AC-16 response time |         "count": 10,
AC-16 response time |         "count": 150,
AC-16 response time |         "count": 40,
AC-16 response time |     "passed": true
AC-16 response time | }
```

## Part 7: Complete test inventory

Output of `uv run pytest --collect-only -q`. These are tests **collected**, not passed. Tests in `tests/acceptance/` other than `test_client_selftest.py` carry the `acceptance` marker (48).

```text
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac01_create_then_retrieve_returns_identical_values[contract-example-ransomware]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac01_create_then_retrieve_returns_identical_values[utc-z-suffix]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac01_create_then_retrieve_returns_identical_values[positive-half-hour-offset]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac01_create_then_retrieve_returns_identical_values[non-ascii-text]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac01_each_incident_gets_a_distinct_id
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[ac02-missing-description]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[ac02-timestamp-without-offset]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[ac02-future-discovery]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[missing-title]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[missing-discovered-at]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[missing-reporter-name]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[empty-title]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[empty-reporter-name]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[malformed-timestamp]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac02_invalid_incident_is_rejected_naming_the_field[title-wrong-type]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac03_unknown_id_get_and_post_return_404[INC-999999]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac03_unknown_id_get_and_post_return_404[does-not-exist-000]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac04_three_technical_items_are_linked_to_the_incident
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac04_evidence_is_not_shared_between_incidents
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac05_evidence_is_stored_and_returned_unchanged[contract-example-business-impact]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac05_evidence_is_stored_and_returned_unchanged[ac04-technical-1]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac05_evidence_is_stored_and_returned_unchanged[ac04-technical-2]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac05_evidence_is_stored_and_returned_unchanged[ac04-technical-3]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac05_evidence_is_stored_and_returned_unchanged[legal]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_ac05_evidence_is_stored_and_returned_unchanged[other]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_invalid_evidence_is_rejected_and_not_attached[unknown-category]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_invalid_evidence_is_rejected_and_not_attached[lowercase-category]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_invalid_evidence_is_rejected_and_not_attached[missing-category]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_invalid_evidence_is_rejected_and_not_attached[empty-summary]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_invalid_evidence_is_rejected_and_not_attached[missing-source]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_invalid_evidence_is_rejected_and_not_attached[collected-at-without-offset]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_invalid_evidence_is_rejected_and_not_attached[missing-collected-at]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_stored_incident_cannot_be_edited_or_deleted[PUT]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_stored_incident_cannot_be_edited_or_deleted[PATCH]
tests/acceptance/test_ac01_05_incidents_evidence.py::test_stored_incident_cannot_be_edited_or_deleted[DELETE]
tests/acceptance/test_ac14_security.py::test_health_is_public
tests/acceptance/test_ac14_security.py::test_authenticated_route_rejects_bad_key[missing-key]
tests/acceptance/test_ac14_security.py::test_authenticated_route_rejects_bad_key[wrong-key]
tests/acceptance/test_ac14_security.py::test_authenticated_route_accepts_valid_key
tests/acceptance/test_ac14_security.py::test_deployment_uses_https
tests/acceptance/test_client_selftest.py::test_client_sends_configured_key
tests/acceptance/test_client_selftest.py::test_client_omits_key_when_missing_even_if_caller_passes_one
tests/acceptance/test_client_selftest.py::test_client_wrong_key_differs_from_valid_key
tests/acceptance/test_client_selftest.py::test_client_refuses_valid_auth_without_api_key
tests/acceptance/test_client_selftest.py::test_client_config_from_env
tests/acceptance/test_system_endpoints.py::test_health_body_has_status
tests/acceptance/test_system_endpoints.py::test_401_uses_error_format[missing-key]
tests/acceptance/test_system_endpoints.py::test_401_uses_error_format[wrong-key]
tests/acceptance/test_system_endpoints.py::test_unknown_incident_get_is_404_with_error_format[INC-999999]
tests/acceptance/test_system_endpoints.py::test_unknown_incident_get_is_404_with_error_format[does-not-exist-000]
tests/acceptance/test_system_endpoints.py::test_reset_requires_key[missing-key]
tests/acceptance/test_system_endpoints.py::test_reset_requires_key[wrong-key]
tests/acceptance/test_system_endpoints.py::test_reset_succeeds_and_is_repeatable
tests/fixtures/test_fixture_data.py::test_case_names_are_unique
tests/fixtures/test_fixture_data.py::test_valid_incident_follows_contract[contract-example-ransomware]
tests/fixtures/test_fixture_data.py::test_valid_incident_follows_contract[utc-z-suffix]
tests/fixtures/test_fixture_data.py::test_valid_incident_follows_contract[positive-half-hour-offset]
tests/fixtures/test_fixture_data.py::test_valid_incident_follows_contract[non-ascii-text]
tests/fixtures/test_fixture_data.py::test_valid_evidence_follows_contract[contract-example-business-impact]
tests/fixtures/test_fixture_data.py::test_valid_evidence_follows_contract[ac04-technical-1]
tests/fixtures/test_fixture_data.py::test_valid_evidence_follows_contract[ac04-technical-2]
tests/fixtures/test_fixture_data.py::test_valid_evidence_follows_contract[ac04-technical-3]
tests/fixtures/test_fixture_data.py::test_valid_evidence_follows_contract[legal]
tests/fixtures/test_fixture_data.py::test_valid_evidence_follows_contract[other]
tests/fixtures/test_fixture_data.py::test_valid_evidence_covers_every_category_and_ac04
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[ac02-missing-description]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[ac02-timestamp-without-offset]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[ac02-future-discovery]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[missing-title]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[missing-discovered-at]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[missing-reporter-name]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[empty-title]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[empty-reporter-name]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[malformed-timestamp]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[title-wrong-type]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[unknown-category]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[lowercase-category]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[missing-category]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[empty-summary]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[missing-source]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[collected-at-without-offset]
tests/fixtures/test_fixture_data.py::test_invalid_case_names_a_real_field[missing-collected-at]
tests/fixtures/test_fixture_data.py::test_ac02_cases_are_present
tests/fixtures/test_fixture_data.py::test_unknown_ids_are_present
tests/infrastructure/test_app_smoke.py::test_app_imports_and_generates_openapi
tests/infrastructure/test_app_smoke.py::test_openapi_endpoint_is_served
tests/infrastructure/test_auth.py::test_health_needs_no_key
tests/infrastructure/test_auth.py::test_bad_key_is_401_in_contract_format[missing]
tests/infrastructure/test_auth.py::test_bad_key_is_401_in_contract_format[wrong]
tests/infrastructure/test_auth.py::test_bad_key_is_401_in_contract_format[empty]
tests/infrastructure/test_auth.py::test_header_name_is_case_insensitive
tests/infrastructure/test_auth.py::test_key_is_checked_before_routing[GET-/incidents/INC-999]
tests/infrastructure/test_auth.py::test_key_is_checked_before_routing[DELETE-/incidents/INC-001]
tests/infrastructure/test_auth.py::test_key_is_checked_before_routing[POST-/incidents]
tests/infrastructure/test_auth.py::test_key_is_checked_before_routing[GET-/no/such/path]
tests/infrastructure/test_auth.py::test_valid_key_reaches_the_app
tests/infrastructure/test_auth.py::test_blank_configured_key_rejects_everything
tests/infrastructure/test_auth.py::test_require_api_key_dependency
tests/infrastructure/test_auth.py::test_responses_carry_request_id_and_commit
tests/infrastructure/test_auth.py::test_docs_declare_the_api_key
tests/infrastructure/test_auth.py::test_documenting_the_key_does_not_change_enforcement
tests/infrastructure/test_database.py::test_ids_have_the_contract_format
tests/infrastructure/test_database.py::test_timestamps_keep_the_instant_and_are_timezone_aware
tests/infrastructure/test_database.py::test_data_survives_a_new_connection_pool
tests/infrastructure/test_database.py::test_reset_clears_everything_and_restarts_ids
tests/infrastructure/test_database.py::test_evidence_cannot_outlive_its_incident
tests/infrastructure/test_errors.py::test_missing_field_is_400_naming_it
tests/infrastructure/test_errors.py::test_bad_value_is_400_naming_the_field
tests/infrastructure/test_errors.py::test_malformed_json_is_400
tests/infrastructure/test_errors.py::test_api_error_from_a_route
tests/infrastructure/test_errors.py::test_unknown_path_is_404_in_contract_format
tests/infrastructure/test_errors.py::test_edit_or_delete_is_405[PUT]
tests/infrastructure/test_errors.py::test_edit_or_delete_is_405[PATCH]
tests/infrastructure/test_errors.py::test_edit_or_delete_is_405[DELETE]
tests/infrastructure/test_errors.py::test_unexpected_errors_hide_internals
tests/infrastructure/test_errors.py::test_custom_validator_message_has_no_pydantic_prefix
tests/infrastructure/test_feature_database.py::test_postgres_create_retrieve_evidence_restart_reset
tests/infrastructure/test_feature_database.py::test_postgres_invalid_incidents_do_not_write[description-]
tests/infrastructure/test_feature_database.py::test_postgres_invalid_incidents_do_not_write[discoveredAt-2020-01-01T10:00:00]
tests/infrastructure/test_feature_database.py::test_postgres_invalid_incidents_do_not_write[discoveredAt-9999-01-01T00:00:00Z]
tests/infrastructure/test_feature_database.py::test_postgres_invalid_incidents_do_not_write[title-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
tests/infrastructure/test_feature_database.py::test_postgres_invalid_evidence_and_unknown_parent
tests/infrastructure/test_feature_routes.py::test_registered_workflow
tests/infrastructure/test_feature_routes.py::test_features_require_shared_auth[None-POST-/incidents]
tests/infrastructure/test_feature_routes.py::test_features_require_shared_auth[None-GET-/incidents/INC-001]
tests/infrastructure/test_feature_routes.py::test_features_require_shared_auth[None-POST-/incidents/INC-001/evidence]
tests/infrastructure/test_feature_routes.py::test_features_require_shared_auth[incorrect-POST-/incidents]
tests/infrastructure/test_feature_routes.py::test_features_require_shared_auth[incorrect-GET-/incidents/INC-001]
tests/infrastructure/test_feature_routes.py::test_features_require_shared_auth[incorrect-POST-/incidents/INC-001/evidence]
tests/infrastructure/test_feature_routes.py::test_shared_errors_and_precedence
tests/infrastructure/test_test_interface.py::test_setup_returns_the_same_id
tests/infrastructure/test_test_interface.py::test_setup_resets_to_an_empty_baseline
tests/infrastructure/test_test_interface.py::test_session_id_can_be_used_once
tests/infrastructure/test_test_interface.py::test_invalid_setup_is_400[empty]
tests/infrastructure/test_test_interface.py::test_invalid_setup_is_400[blank-id]
tests/infrastructure/test_test_interface.py::test_invalid_setup_is_400[whitespace-id]
tests/infrastructure/test_test_interface.py::test_invalid_setup_is_400[number-id]
tests/infrastructure/test_test_interface.py::test_invalid_setup_is_400[bad-setup]
tests/infrastructure/test_test_interface.py::test_invalid_setup_is_400[too-long]
tests/infrastructure/test_test_interface.py::test_setup_body_that_is_not_json_is_400
tests/infrastructure/test_test_interface.py::test_setup_without_setup_field_is_accepted
tests/infrastructure/test_test_interface.py::test_test_endpoints_need_the_key_and_say_where_errors_come_from
tests/infrastructure/test_test_interface.py::test_report_for_unknown_session_is_404
tests/infrastructure/test_test_interface.py::test_report_without_session_id_is_400
tests/infrastructure/test_test_interface.py::test_report_has_the_spec_shape
tests/infrastructure/test_test_interface.py::test_reading_the_report_runs_no_project_operations
tests/infrastructure/test_test_interface.py::test_real_coverage_counts_lines_per_session
tests/scripts/test_scripts.py::test_summary_passes_at_exactly_95_percent
tests/scripts/test_scripts.py::test_summary_counts_errors_as_misses_even_when_fast
tests/scripts/test_scripts.py::test_summary_rejects_empty_run
tests/scripts/test_scripts.py::test_plan_has_requested_size_mix_and_is_reproducible
tests/scripts/test_scripts.py::test_synthetic_incidents_are_distinct_and_valid_length
tests/scripts/test_scripts.py::test_compare_accepts_same_instant_in_utc
tests/scripts/test_scripts.py::test_compare_reports_changed_fields
tests/tester/test_report.py::test_acceptance_criteria_mapping
tests/tester/test_report.py::test_outcomes_follow_the_spec
tests/tester/test_report.py::test_no_response_is_a_communication_error
tests/tester/test_report.py::test_target_5xx_is_a_system_error
tests/tester/test_report.py::test_fixture_failure_is_a_tester_error
tests/tester/test_report.py::test_every_planned_test_appears_once_with_a_message
tests/tester/test_report.py::test_abort_marks_running_test_error_and_rest_skip
tests/tester/test_report.py::test_coverage_fields
tests/tester/test_service.py::test_setup_creates_a_uuid_session_and_prepares_the_target
tests/tester/test_service.py::test_bad_target_is_400[not-approved]
tests/tester/test_service.py::test_bad_target_is_400[not-http]
tests/tester/test_service.py::test_bad_target_is_400[query]
tests/tester/test_service.py::test_bad_target_is_400[test-suffix]
tests/tester/test_service.py::test_bad_target_is_400[empty]
tests/tester/test_service.py::test_bad_target_is_400[number]
tests/tester/test_service.py::test_system_setup_failure_is_forwarded_unchanged
tests/tester/test_service.py::test_wrong_session_id_from_system_is_rejected
tests/tester/test_service.py::test_unreachable_system_is_a_communication_error
tests/tester/test_service.py::test_run_returns_and_stores_the_report
tests/tester/test_service.py::test_a_session_runs_once
tests/tester/test_service.py::test_abort_returns_500_and_keeps_available_results
tests/tester/test_service.py::test_bad_requests[post-/test/run-body0-404]
tests/tester/test_service.py::test_bad_requests[post-/test/run-body1-400]
tests/tester/test_service.py::test_bad_requests[get-/test/report?session_id=nope-None-404]
tests/tester/test_service.py::test_bad_requests[get-/test/report-None-400]
tests/unit/test_evidence.py::test_attach_and_retrieve
tests/unit/test_evidence.py::test_missing_evidence_no_write[category]
tests/unit/test_evidence.py::test_missing_evidence_no_write[summary]
tests/unit/test_evidence.py::test_missing_evidence_no_write[source]
tests/unit/test_evidence.py::test_missing_evidence_no_write[collectedAt]
tests/unit/test_evidence.py::test_invalid_evidence_no_write[category-INVALID]
tests/unit/test_evidence.py::test_invalid_evidence_no_write[summary- ]
tests/unit/test_evidence.py::test_invalid_evidence_no_write[source-]
tests/unit/test_evidence.py::test_invalid_evidence_no_write[collectedAt-2020-01-01T00:00:00]
tests/unit/test_evidence.py::test_unknown_parent
tests/unit/test_evidence.py::test_unknown_parent_precedes_body_validation[{]
tests/unit/test_evidence.py::test_unknown_parent_precedes_body_validation[{}]
tests/unit/test_evidence.py::test_unknown_parent_precedes_body_validation[null]
tests/unit/test_evidence.py::test_unknown_parent_precedes_body_validation["invalid body"]
tests/unit/test_evidence.py::test_invalid_body_for_existing_parent[{]
tests/unit/test_evidence.py::test_invalid_body_for_existing_parent[{}]
tests/unit/test_evidence.py::test_invalid_body_for_existing_parent[null]
tests/unit/test_evidence.py::test_invalid_body_for_existing_parent["invalid body"]
tests/unit/test_evidence.py::test_evidence_error_names_field
tests/unit/test_evidence.py::test_evidence_request_schema_in_openapi
tests/unit/test_incidents.py::test_create_retrieve_and_unique_ids
tests/unit/test_incidents.py::test_missing_fields_leave_no_records[title]
tests/unit/test_incidents.py::test_missing_fields_leave_no_records[description]
tests/unit/test_incidents.py::test_missing_fields_leave_no_records[discoveredAt]
tests/unit/test_incidents.py::test_missing_fields_leave_no_records[reporterName]
tests/unit/test_incidents.py::test_invalid_input_no_write[description-]
tests/unit/test_incidents.py::test_invalid_input_no_write[title-  ]
tests/unit/test_incidents.py::test_invalid_input_no_write[discoveredAt-2020-01-01T00:00:00]
tests/unit/test_incidents.py::test_invalid_input_no_write[discoveredAt-9999-01-01T00:00:00Z]
tests/unit/test_incidents.py::test_invalid_input_no_write[discoveredAt-bad]
tests/unit/test_incidents.py::test_unknown_incident
tests/unit/test_incidents.py::test_malformed_json_and_append_only
tests/unit/test_incidents.py::test_validation_errors_name_field[description-]
tests/unit/test_incidents.py::test_validation_errors_name_field[discoveredAt-2020-01-01T00:00:00]
tests/unit/test_incidents.py::test_validation_errors_name_field[discoveredAt-9999-01-01T00:00:00Z]
tests/unit/test_repository.py::test_create_rolls_back_failed_insert
tests/unit/test_repository.py::test_attach_missing_parent_never_inserts
tests/unit/test_schemas.py::test_missing_incident_fields[title]
tests/unit/test_schemas.py::test_missing_incident_fields[description]
tests/unit/test_schemas.py::test_missing_incident_fields[discoveredAt]
tests/unit/test_schemas.py::test_missing_incident_fields[reporterName]
tests/unit/test_schemas.py::test_invalid_text[-title]
tests/unit/test_schemas.py::test_invalid_text[-description]
tests/unit/test_schemas.py::test_invalid_text[-reporterName]
tests/unit/test_schemas.py::test_invalid_text[ \t\n-title]
tests/unit/test_schemas.py::test_invalid_text[ \t\n-description]
tests/unit/test_schemas.py::test_invalid_text[ \t\n-reporterName]
tests/unit/test_schemas.py::test_invalid_text[123-title]
tests/unit/test_schemas.py::test_invalid_text[123-description]
tests/unit/test_schemas.py::test_invalid_text[123-reporterName]
tests/unit/test_schemas.py::test_invalid_text[None-title]
tests/unit/test_schemas.py::test_invalid_text[None-description]
tests/unit/test_schemas.py::test_invalid_text[None-reporterName]
tests/unit/test_schemas.py::test_invalid_discovery[2020-01-01T10:00:00]
tests/unit/test_schemas.py::test_invalid_discovery[9999-01-01T00:00:00Z]
tests/unit/test_schemas.py::test_invalid_discovery[bad]
tests/unit/test_schemas.py::test_incident_utc_and_aliases
tests/unit/test_schemas.py::test_categories[TECHNICAL]
tests/unit/test_schemas.py::test_categories[BUSINESS_IMPACT]
tests/unit/test_schemas.py::test_categories[LEGAL]
tests/unit/test_schemas.py::test_categories[OTHER]
tests/unit/test_schemas.py::test_missing_evidence[category]
tests/unit/test_schemas.py::test_missing_evidence[summary]
tests/unit/test_schemas.py::test_missing_evidence[source]
tests/unit/test_schemas.py::test_missing_evidence[collectedAt]
tests/unit/test_schemas.py::test_invalid_evidence[category-INVALID]
tests/unit/test_schemas.py::test_invalid_evidence[summary-]
tests/unit/test_schemas.py::test_invalid_evidence[source-  ]
tests/unit/test_schemas.py::test_invalid_evidence[collectedAt-2020-01-01T00:00:00]
tests/unit/test_schemas.py::test_invalid_evidence[collectedAt-bad]
tests/unit/test_schemas.py::test_future_evidence_is_allowed
tests/unit/test_schemas.py::test_response_shapes
tests/unit/test_schemas.py::test_non_contract_timestamp_formats[1577887200_0]
tests/unit/test_schemas.py::test_non_contract_timestamp_formats[1577887200_1]
tests/unit/test_schemas.py::test_non_contract_timestamp_formats[2020-01-01_10:00:00Z]
tests/unit/test_schemas.py::test_non_contract_timestamp_formats[2020-01-01T10:00Z]
tests/unit/test_schemas.py::test_non_contract_timestamp_formats[2020-01-01T10:00:00+0400]
tests/unit/test_schemas.py::test_existing_storage_limits[title-200]
tests/unit/test_schemas.py::test_existing_storage_limits[description-5000]
tests/unit/test_schemas.py::test_existing_storage_limits[reporterName-500]
tests/unit/test_schemas.py::test_existing_source_storage_limit

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/mohitmanna/Desktop/Projects/sec-project-ece30861/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
260 tests collected in 0.60s
```

## Part 8: Submission drafts as committed

### `docs/submission/mohit-gradescope-ready.md`

```markdown
# Phase 3 Gradescope answers: Q4, Q6, Q7 (paste-ready)

Owner: Mohit. Compiled 2026-10-18, 21:55 EDT (2026-10-19 01:55 UTC).

Sources: `docs/test-results/`, `docs/cross-team-testing.md`, `docs/contract-issues.md`, CI runs on GitHub, and live HTTP checks.

The exact Phase 3 rubric wording wasn't available locally. The subsections follow the team README (section 9) and the Phase 2 pod spec. Check each sentence limit against the Gradescope form before pasting.

Items marked **PENDING** are not done. The class registry entry was confirmed submitted by the team on 2026-10-18. Google Cloud hosting was confirmed acceptable. Don't paste them as if they were.

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
```

### `docs/submission/README.md`

```markdown
# Phase 3 submission

Section ownership:

| Section | Lead |
| --- | --- |
| Q1 Delivered increment | Astha |
| Q2 Deployment and operation | Srihari |
| Q3 Interface conformance | Srihari |
| Q4 Automated validation | Mohit |
| Q5 Updated models | Astha |
| Q6 Cross-team readiness | Mohit |
| Q7 Status and limitations | All (Mohit consolidates) |
| Q8 Actual GenAI use | All |
| Q9 References | All (Astha consolidates) |

Record real observations only. See section 9 of the root README for the evidence expected in each section.
```

### `docs/submission/q2-deployment.md`

```markdown
# Q2 Deployment and operation (draft)

Lead: Srihari. Everything below was observed on 2026-10-18 unless noted.
Operating details: `docs/deployment.md`.

## Host and runtime

- **Host:** Google Cloud Run (managed containers), project
  `ece30861-project-62ca4b`, region `us-central1`.
- **Runtime:** one Docker image (`Dockerfile`): Python 3.12, FastAPI served by
  Uvicorn, dependencies installed from the locked `uv.lock`, running as a
  non-root user. 1 vCPU, 512 MiB, min 1 / max 1 instances (`scripts/deploy_gcp.sh`
  since `6d88509`, so a test session's in-memory coverage stays on one
  instance). One instance is kept warm so no request waits for a cold start (REQ-15).
- **Database:** Cloud SQL for PostgreSQL 16 (`db-f1-micro`, 10 GB SSD),
  connected through Cloud Run's built-in Cloud SQL connector. It is separate
  from the app, so app restarts and redeploys don't touch the data.
- **HTTPS:** provided by Cloud Run with a Google-managed certificate. Plain
  `http://` gets a 302 redirect to `https://`. AC-14's HTTPS check passes
  against the deployment.

## Deployed URL

- **Base URL:** https://incident-api-356019173418.us-central1.run.app
- **Public endpoint:** `GET /health` → `200 {"status": "OK"}` (75 ms when checked).
- Every other endpoint needs the shared test key in `X-API-Key`.

## Commit mapping

Every response carries an `X-App-Commit` header with the git commit the
running image was built from. Images are built from a clean `git archive` of
the ref, tagged with the commit (`.../incident-api/api:<commit>`), and deployed
with `scripts/deploy_gcp.sh`.

```sh
curl -sI https://incident-api-356019173418.us-central1.run.app/health | grep -i x-app-commit
```

- **Deployed commit:** `f551649` (`integration` branch), deployed 2026-10-18
  and checked with the header above. It adds the course testing interface
  (`/test/setup`, `/test/report`); our tester ran all 48 acceptance tests
  against it, all passing (`docs/cross-team-testing.md`). The previous
  deployment, `ed5f449`, also passed 48 acceptance tests.
  The persistence and performance runs below were against an earlier
  deployment, `f2b607c`. The incident and evidence routes are the same, but
  `f551649` also adds the testing interface, migration 0002, coverage
  instrumentation and max instances 1. AC-16 hasn't been re-run on `f551649`
  (`docs/test-results/2026-10-18-deployed-f551649.md`).

## Secrets

- `DATABASE_URL` and `API_KEY` are stored in Google Secret Manager and given
  to the service as environment variables at start. They are not in git,
  images, logs or this report. `.env` is git-ignored; `.env.example` has
  placeholders only. The database password and API key were randomly generated.
- The API key is compared in constant time; a blank configured key rejects every
  request instead of disabling authentication.
- **Sharing the test key:** project members read it with
  `gcloud secrets versions access latest --secret api-key`. It is shared with
  teammates and the other team over a private channel only.

## Persistence, startup and restart

- On start the container applies pending migrations (`alembic upgrade head`),
  then serves (`scripts/start.sh`). Already-applied migrations are skipped.
- Data stays until `POST /reset`, which clears evidence and incidents in one
  transaction and restarts the IDs at `INC-001`.
- **Restart procedure:** roll out a new revision of the same image
  (`gcloud run services update incident-api ... --update-env-vars RESTARTED_AT=<time>`),
  which replaces the running instances. See `docs/deployment.md`.
- **Restart check (deployed):** `scripts/check_persistence.py` created 100
  incidents, the service was restarted (revision `incident-api-00002-msv` →
  `incident-api-00003-ggj`) without a reset, and `verify` found **100/100
  incidents intact**. `reset` then removed all 100.
- Local check (2026-10-16): the same behaviour with `docker compose restart app`.

## Validation against earlier deployments (2026-10-18: acceptance on `ed5f449`, AC-16 on `f2b607c`)

| Check | Result |
| --- | --- |
| Acceptance suite (`pytest -m acceptance`, AC-01 to AC-05, AC-14) | **48 passed**, 0 failed, 0 skipped |
| Restart persistence (AC-16) | 100/100 incidents intact after restart; all 100 created IDs gave 404 after reset |
| Performance (AC-16): 100 incidents loaded, 200 sequential requests from a laptop | **200/200 within 1 s** (needs 95%); p50 48 ms, p95 61 ms, max 76 ms; 0 errors |

One unexplained event: on the first persistence run, one request timed out on
the client side (10 s), so that run was repeated. Cloud Run's request logs for
that period show no request slower than 0.36 s, which suggests a delay on the
network path between the laptop and Google rather than in the service. That
wasn't confirmed. It did not recur.

## Logging

One line per request: request ID, method, path, status, duration, and any
record IDs in the path. Headers (which carry the API key) and request/response
bodies (which carry incident details) are never logged. The request ID is also
returned in `X-Request-Id`, so a client-side failure can be matched to its log
line. Logs go to Google Cloud Logging.

Sanitized excerpt from the **deployed** service (2026-10-18, commit `f2b607c`):
health check, `/reset` without and with the key, create an incident, add
evidence, get it, and a delete attempt (405).

```
2026-10-18 19:40:22,869 INFO app.requests request_id=ba4ccca74e1d method=GET path=/health status=200 duration_ms=51.6 ids=-
2026-10-18 19:40:23,177 INFO app.requests request_id=be1d4edd1d95 method=POST path=/reset status=401 duration_ms=0.5 ids=-
2026-10-18 19:40:23,608 INFO app.requests request_id=0785fb07db62 method=POST path=/reset status=200 duration_ms=340.3 ids=-
2026-10-18 19:40:23,736 INFO app.requests request_id=e99251818bbb method=POST path=/incidents status=201 duration_ms=28.5 ids=-
2026-10-18 19:40:23,858 INFO app.requests request_id=1064e8509aa6 method=POST path=/incidents/INC-001/evidence status=201 duration_ms=28.2 ids=INC-001
2026-10-18 19:40:23,965 INFO app.requests request_id=382ff3c35fc9 method=GET path=/incidents/INC-001 status=200 duration_ms=12.9 ids=INC-001
2026-10-18 19:40:24,094 INFO app.requests request_id=7a4f9e667048 method=DELETE path=/incidents/INC-001 status=405 duration_ms=0.7 ids=INC-001
```

## Registry and documentation

- **Class registry entry:** system base URL above; tester
  https://incident-tester-356019173418.us-central1.run.app (values in
  `docs/cross-team-testing.md`). Submitted (confirmed by the team, 2026-10-18).
- **Test runner:** `tests/acceptance/` (Mohit). Run with
  `BASE_URL=<url> API_KEY=<key> uv run pytest -m acceptance`.
- **Docs:** `docs/deployment.md` (operating the deployment), `docs/setup.md`
  (local setup), `migrations/README.md`.

## Cost

About $20–25/month (Cloud SQL plus one warm instance), on the project's own
free-trial billing; a $50 budget sends alerts at 50%, 100% and forecast 100%.
```

### `docs/submission/q3-interface-conformance.md`

```markdown
# Q3 Interface conformance (draft)

Lead: Srihari. Feature details: Astha. Test results: Mohit.

Status of every operation in the pod's common contract (Phase 2 - Pod.pdf,
Q5.1–Q5.3) in the code on the `integration` branch, as of 2026-10-17
(local run on 2026-10-17: 168 unit/infrastructure tests and 47 acceptance tests passed. CI on the deployed commit `f551649`: 212 non-acceptance tests and 47 acceptance tests passed. Against the deployment on 2026-10-18: 48 acceptance tests passed on `ed5f449`, and 48 passed through our tester on `f551649`). "Yes" means implemented
and covered by a test that passes; the deployed run is recorded in
`docs/test-results/2026-10-18-deployed.md`.

**Update this table as Astha's routes land and as deployed runs are recorded.**
Record real observations only (README §9).

## Operations

| Operation | Contract requirement | Phase | Status | Evidence |
| --- | --- | --- | --- | --- |
| `GET /health` | Public; `200 {status: string}` | 3 | **Yes** | `tests/infrastructure/test_auth.py::test_health_needs_no_key`; AC-14 `test_health_is_public` (local run) |
| `POST /reset` | API key; clears all data; `200 {"status": "RESET_COMPLETE"}` | 3 | **Yes** | `tests/infrastructure/test_database.py::test_reset_clears_everything_and_restarts_ids` |
| `POST /incidents` | Create; `201 {incidentId, status: OPEN}`; 400 naming the bad field | 3 | **Yes** | `tests/acceptance/test_ac01_05_incidents_evidence.py` (AC-01/02), `tests/unit/test_incidents.py`; local run 2026-10-17 |
| `GET /incidents/{incidentId}` | Incident with evidence, `currentDecision`/`filing` null; 404 if unknown | 3 | **Yes** | `test_ac01_05_incidents_evidence.py` (AC-01/03/04) |
| `POST /incidents/{incidentId}/evidence` | `201 {evidenceId, recordedAt}`; 404 for unknown incident | 3 | **Yes** | `test_ac01_05_incidents_evidence.py` (AC-04/05), `tests/unit/test_evidence.py` |
| `POST /incidents/{incidentId}/decisions` | Materiality decision, state rules, deadline | 4 | **No**, planned for Phase 4 | — |
| `POST /incidents/{incidentId}/corrections` | Correct the current decision | 4 | **No**, planned for Phase 4 | — |
| `GET /incidents/{incidentId}/deadline-status` | `NOT_APPLICABLE` / `PENDING` / `OVERDUE`, optional `as_of` | 4 | **No**, planned for Phase 4 | — |
| `POST /incidents/{incidentId}/filing` | Record 8-K filing, `ON_TIME`/`LATE` | 4 | **No**, planned for Phase 4 | — |
| `GET /incidents/{incidentId}/timeline` | Events and evidence counts | 4/5 | **No**, planned | — |
| `POST /test/setup` (course testing interface) | API key; `201 {session_id}`; resets to empty baseline; 409 on reused ID | 3 | **Yes** | `tests/infrastructure/test_test_interface.py`; live tester run 2026-10-18 (`docs/cross-team-testing.md`) |
| `GET /test/report` (course testing interface) | API key; code coverage for the session; 404 unknown | 3 | **Yes** | `tests/infrastructure/test_test_interface.py`; live tester run 2026-10-18 |
| `GET /incidents` (proposed, not in contract) | List incidents (needed by AC-02, AC-16) | — | **Not in contract**; currently returns 405 (only POST exists on `/incidents`). Proposal pending pod agreement | `docs/contract-issues.md` #2 |

## Cross-cutting rules

| Contract rule | Status | Evidence |
| --- | --- | --- |
| `X-API-Key` on every endpoint except `/health`; missing/wrong → 401 (REQ-13) | **Yes** | `test_auth.py`; AC-14 `test_authenticated_route_*` (9 passed locally against Docker) |
| Key checked before routing, body validation or lookup (contract-issues #4, our decision) | **Yes** | `test_auth.py::test_key_is_checked_before_routing` |
| Every error is `{"error": CODE, "message": ...}` (REQ-14) | **Yes** | `test_errors.py::assert_error_format` and the tests that use it |
| Validation failures are 400 naming the field, not 422 (REQ-02, AC-02) | **Yes** | `test_errors.py`; per-route in `tests/unit/test_incidents.py`, `test_evidence.py` and AC-02 acceptance tests. E.g. a future `discoveredAt` → `{"error": "INVALID_DISCOVERED_AT", "message": "discoveredAt: Discovery time must not be in the future"}` |
| Unknown resource → 404 (AC-03) | **Yes** | `test_errors.py`; AC-03 acceptance tests |
| Edit/delete attempts → 405 (REQ-07) | **Yes** | `test_errors.py::test_edit_or_delete_is_405`; `DELETE`/`PUT /incidents/INC-001` → 405 (checked 2026-10-17 against the combined app) |
| Wrong-state operations → 409 (REQ-08) | **No**, Phase 4 (no state-changing operations yet) | — |
| Requests RFC 3339 with offset; responses in UTC (REQ-14) | **Yes** | `discoveredAt: 2026-09-21T14:30:00-04:00` comes back as `2026-09-21T18:30:00Z`; `tests/unit/test_schemas.py`, `test_database.py::test_timestamps_keep_the_instant_and_are_timezone_aware` |
| IDs `INC-001` / `EVD-001` | **Yes** (database-generated) | `test_database.py::test_ids_have_the_contract_format` |
| Data kept across restarts until reset (REQ-15) | **Yes**, deployed (`f2b607c`; not re-run on `f551649`) | 2026-10-18: 100/100 incidents intact after a Cloud Run restart (new revision); all created IDs gave 404 after reset (`scripts/check_persistence.py`) |
| 95% of requests within 1 s at 100 incidents (REQ-15) | **Yes**, deployed (`f2b607c`; not re-run on `f551649`) | 2026-10-18: 200/200 within 1 s; p50 48 ms, p95 61 ms (`scripts/performance.py`) |
| Deployed over HTTPS (REQ-13) | **Yes** | https://incident-api-356019173418.us-central1.run.app; AC-14 `test_deployment_uses_https` passes; `http://` redirects to `https://` |

## Our choices where the contract is silent

These are applied by our service; they should be confirmed with the other team
so both implementations behave the same (see `docs/contract-issues.md`).

- **Error codes**: `UNAUTHORIZED` (401), `NOT_FOUND` (404),
  `METHOD_NOT_ALLOWED` (405), `INTERNAL_ERROR` (500), and
  `INVALID_<FIELD>` for 400s (e.g. `INVALID_DISCOVERED_AT`), following the
  contract's only example, `INVALID_DECISION`. A malformed JSON body is
  `INVALID_BODY`.
- **Precedence**: the API key is checked before anything else.
- **Field lengths**: `title` ≤ 200 and `description` ≤ 5000 characters, as
  placeholders in `app/config.py` until the pod agrees (contract-issues #3).
- **IDs after reset** restart at `INC-001` / `EVD-001`, so test runs are
  repeatable.
```

The Q4, Q6 and Q7 drafts contain the same text as the matching sections of `mohit-gradescope-ready.md` above.

## Part 9: Test-result records as committed

### `docs/test-results/README.md`

```markdown
# Test results

Owner: Mohit. Feeds submission Q4 and Q6.

Record real runs only. For each run, include: commit/tag, date, target (local, our deployment, or the other team's deployment), totals, failures, skips, and issue owners.

## Runs

| Date | Target | Result |
| --- | --- | --- |
| 2026-10-16 | Local Docker Compose (`f6b8df6`) | [AC-16 and acceptance, all passing](2026-10-16-local-ac16.md) |
| 2026-10-18 | Our deployment, earlier versions (`ed5f449` / `f2b607c`) | [48 passed acceptance; 100/100 persisted; 200/200 under 1 s](2026-10-18-deployed.md) |
| 2026-10-18 | Our deployment, final version `f551649` | [Tester run by Srihari: 48 pass. Keyless subset by Mohit: 7 passed, 41 skipped. AC-16 not re-run](2026-10-18-deployed-f551649.md) |
| 2026-10-18 | Other team's deployment (incident-clock) | [Our suite: 45 passed, 0 failed, 3 skipped (reset tests, on purpose)](2026-10-18-cross-team-ours-on-theirs.md) |

CI also runs the acceptance suite and an AC-16 smoke test (persistence across an app restart, reset, response time) against an app inside the CI job on every push. Those runs are regression checks, not recorded results.
```

### `docs/test-results/traceability.md`

```markdown
# Requirement / test traceability

Owner: Mohit. Feeds submission Q4.

This table covers local, CI and deployed runs, and each run is recorded in this folder. "Final" means the deployed commit `f551649`. "Earlier" means `ed5f449` (acceptance) or `f2b607c` (AC-16).

| Criterion | Tests | Status |
| --- | --- | --- |
| AC-01 (REQ-01, REQ-14) | `test_ac01_create_then_retrieve_returns_identical_values[4]`, `test_ac01_each_incident_gets_a_distinct_id` | Pass: CI, earlier, and final (via tester) |
| AC-02 (REQ-02, REQ-14) | `test_ac02_invalid_incident_is_rejected_naming_the_field[10]` (black box: 400 naming the field) | Pass: CI, earlier, final (via tester) |
| AC-02 "count unchanged" | No list route (issue #2). DB-level evidence: `tests/infrastructure/test_feature_database.py::test_postgres_invalid_incidents_do_not_write` (PostgreSQL row counts stay 0), `tests/unit/test_incidents.py::test_missing_fields_leave_no_records`, `test_invalid_input_no_write` | DB tests pass in CI. Not checkable over HTTP until issue #2 is settled |
| AC-02 max length | Waits on issue #3. Only our placeholder (title > 200) is tested at DB level | Open |
| AC-03 (REQ-14) | `test_ac03_unknown_id_get_and_post_return_404[2]`, `test_unknown_incident_get_is_404_with_error_format[2]` | Pass: CI, earlier, final (via tester) |
| AC-04 (REQ-03) | `test_ac04_three_technical_items_are_linked_to_the_incident`, `test_ac04_evidence_is_not_shared_between_incidents` | Pass: CI, earlier, final (via tester) |
| AC-05 (REQ-03) | `test_ac05_evidence_is_stored_and_returned_unchanged[6]`, `test_invalid_evidence_is_rejected_and_not_attached[7]` | Pass: CI, earlier, final (via tester) |
| AC-08, REQ-07 half only | `test_stored_incident_cannot_be_edited_or_deleted[PUT, PATCH, DELETE]` | Pass. Correction history (REQ-06) isn't implemented or tested, so AC-08 as a whole isn't met |
| AC-14 (REQ-13) | `test_health_is_public`, `test_health_body_has_status`, `test_authenticated_route_rejects_bad_key[missing, wrong]`, `test_authenticated_route_accepts_valid_key`, `test_401_uses_error_format[2]`, `test_deployment_uses_https` | Pass: CI (HTTPS skipped), earlier, final via tester, and final keyless by Mohit (7 passed) |
| AC-16 reset | `test_reset_requires_key[2]`, `test_reset_succeeds_and_is_repeatable` (destructive, opt-in); `scripts.check_persistence reset` | Pass: CI, earlier, final (via tester). Per-ID 404 checks only cover the IDs we created. Table-level proof is `tests/infrastructure/test_database.py::test_reset_clears_everything_and_restarts_ids` (CI) |
| AC-16 restart persistence | `scripts.check_persistence create` / restart / `verify` | Local 100/100 (app and full stack). CI 100/100. Earlier `f2b607c` 100/100. **Not run on final** |
| AC-16 response time | `scripts.performance` (200 requests, 100 incidents) | Local 200/200. CI 200/200 (loopback). Earlier `f2b607c` 200/200, p95 61 ms. **Not run on final** |
| AC-06, 07, 09 to 13, 15 | None | Phase 4/5 operations not implemented |

Before any service existed, the AC-14 tests were checked two ways. Against a throwaway local stub with `/health` and key checking, they passed (HTTPS check skipped). Against the bare scaffold with no routes, they failed as expected. Later, against a build without the incident routes, 33 of 35 AC-01 to AC-05 tests failed. The 2 that passed are 404 checks, which a missing route also satisfies.
```

### `docs/test-results/2026-10-16-local-ac16.md`

```markdown
# 2026-10-16: local AC-16 and acceptance run (Docker Compose)

Owner: Mohit. **Target: a local Docker Compose stack, not a deployment.** These results show that the code and scripts work. They don't replace the AC-16 run against the deployed service.

## Conditions

| | |
| --- | --- |
| Date | 2026-10-16, 21:04 local (2026-10-17T02:04Z) |
| Server code | `integration` at `f6b8df6` (Astha's PR #4 and Mohit's PR #5 merged), built with `docker compose up --build` |
| Database | `postgres:16` in Compose, named volume |
| Client | Same machine (Darwin arm64, Python 3.12.1). Scripts from the commit that adds them, run against the server above |
| Network | Loopback (`http://127.0.0.1:8000`), so no network latency is included |

## Results

| Check | How | Result |
| --- | --- | --- |
| Restart persistence (app) | `check_persistence create` (100 incidents), `docker compose restart app`, then `verify` | **100/100 intact** |
| Restart persistence (whole stack) | `docker compose down` (volume kept), `up`, then `verify` | **100/100 intact** |
| Response time | `scripts.performance`: 100 more incidents loaded (0.7 s), then 200 sequential requests (150 GET incident, 40 POST evidence, 10 GET health), seed 30861 | **200/200 within 1 s (100%; target 95%)**, 0 errors. p50 6.4 ms, p95 16.1 ms, max 31.4 ms |
| Reset | `check_persistence reset`: `POST /reset`, then GET each of the 100 IDs | **100/100 return 404** |
| Acceptance suite | `pytest -m acceptance` with `ALLOW_DESTRUCTIVE_TESTS=1` | **47 passed, 1 skipped** (HTTPS check skips for a local target) |

## Caveats

- "No incidents remain after reset" is checked per ID, because there's no list route (`docs/contract-issues.md` #2).
- The latency numbers are loopback figures and say nothing about the deployed host. Re-run `scripts.performance` against the deployment and record it as a separate result.
```

### `docs/test-results/2026-10-18-deployed.md`

```markdown
# 2026-10-18: acceptance and AC-16 runs against earlier deployments (`ed5f449`, `f2b607c`)

These are **not** the final version. For `f551649`, see [2026-10-18-deployed-f551649.md](2026-10-18-deployed-f551649.md).

Owner: Mohit. **Target: our deployed service**, https://incident-api-356019173418.us-central1.run.app (Google Cloud Run + Cloud SQL, see `docs/deployment.md`).

The suite and scripts are Mohit's (`tests/acceptance/`, `scripts/`). Srihari ran them against the deployment, because the shared test key lives in Secret Manager and he has `gcloud` set up. His numbers are copied from `docs/submission/q2-deployment.md`. Mohit's own checks below need no key.

## Conditions

| | |
| --- | --- |
| Date | 2026-10-18 |
| Server code | Acceptance suite: `ed5f449` (`integration`). Persistence and performance: `f2b607c`. The incident and evidence routes are the same in both; `ed5f449` adds deployment scripts, `X-App-Commit` and the `/docs` Authorize button |
| How the commit was checked | `X-App-Commit` response header |
| Client | A laptop over the public internet, so network latency is included |

## Results (run by Srihari)

| Check | How | Result |
| --- | --- | --- |
| Acceptance suite | `pytest -m acceptance` with `ALLOW_DESTRUCTIVE_TESTS=1` | **48 passed**, 0 failed, 0 skipped. The HTTPS check ran and passed |
| Restart persistence | `check_persistence create` (100 incidents), new Cloud Run revision (`incident-api-00002-msv` → `incident-api-00003-ggj`), then `verify` | **100/100 intact** |
| Reset | `check_persistence reset` | All 100 created IDs return 404. This doesn't prove no other records remain; see the caveats |
| Response time | `scripts.performance`: 100 incidents, 200 sequential requests | **200/200 within 1 s** (target 95%), 0 errors. p50 48 ms, p95 61 ms, max 76 ms |

On the first persistence run, one request hit the client's 10 s timeout, so the run was repeated. Cloud Run's logs for that period show no request slower than 0.36 s, which suggests a network delay rather than the service. That wasn't confirmed. It didn't happen again.

## Spot checks without the key (run by Mohit, 2026-10-18)

| Request | Expected | Observed |
| --- | --- | --- |
| `GET /health` | 200 `{"status": ...}`, no key needed | 200 `{"status":"OK"}` |
| `GET http://…/health` | Redirect to HTTPS | 302 to `https://…/health` |
| `GET /incidents/INC-001` with no key | 401 `{error, message}` | 401 `{"error":"UNAUTHORIZED","message":"missing or invalid API key"}` |
| `GET /incidents/INC-001` with a wrong key | 401 `{error, message}` | 401, same body |
| `X-App-Commit` header | The deployed commit | `ed5f449` |

## Caveats

- "No incidents remain after reset" is only checked for the IDs the script created, because there's no list route (`docs/contract-issues.md` #2). The proof that tables are empty after a reset is the DB-level test `tests/infrastructure/test_database.py::test_reset_clears_everything_and_restarts_ids`, which runs in CI.
- Response times come from one laptop at one time of day. They show the target is met with plenty of margin, not what every client will see.
- Mohit hasn't run the keyed suite himself yet. That needs the key from Srihari over a private channel.
```

### `docs/test-results/2026-10-18-deployed-f551649.md`

```markdown
# 2026-10-18: results against the final deployment `f551649`

Owner: Mohit. **Target: our deployed system**, https://incident-api-356019173418.us-central1.run.app, reporting `X-App-Commit: f551649` before and after the run.

## 1. Full suite through our deployed tester (run by Srihari)

Srihari ran Mohit's acceptance suite against `f551649` through our tester (https://incident-tester-356019173418.us-central1.run.app), using the course testing interface. The source is `docs/cross-team-testing.md`, "Live check".

| | |
| --- | --- |
| Date | 2026-10-18 (exact time not recorded) |
| Steps | `POST /test/setup` (resets the system), `POST /test/run`, `GET /test/report` |
| Tests | 48 acceptance tests, reset tests included |
| Result | **48 pass, 0 fail** |
| Code coverage | 135 of 522 lines of the `app` package, taken from the system's `/test/report` |
| Component coverage | null; the pod spec defines no component list |
| System coverage | 8 of 16 ACs had at least one test run: AC-01, 02, 03, 04, 05, 08, 14, 16. "Exercised" doesn't mean fully satisfied. AC-08 only covers the REQ-07 edit/delete half, and AC-16 only covers the reset tests, not restart or timing |

## 2. Keyless subset (run by Mohit)

| | |
| --- | --- |
| Date | 2026-10-18 21:55 EDT (2026-10-19 01:55 UTC) |
| Suite commit | `a520f25` (`integration`) |
| Command | `BASE_URL=https://incident-api-356019173418.us-central1.run.app uv run pytest -m acceptance` with `API_KEY` unset and `ALLOW_DESTRUCTIVE_TESTS` unset |
| Result | **7 passed, 0 failed, 41 skipped** |

The 7 that passed:
- `test_health_is_public`
- `test_health_body_has_status`
- `test_authenticated_route_rejects_bad_key[missing]` and `[wrong]`
- `test_401_uses_error_format` (2)
- `test_deployment_uses_https`

39 tests skipped because they need a valid key, and 2 because they're destructive. Mohit had no authorized key on his machine: there's no `.env` and no `gcloud`.

## 3. Not run on `f551649`

- **AC-16 restart persistence and the 200-request timing script.** They need the key, a Cloud Run revision restart and a reset, and Srihari coordinates all three (`docs/deployment.md`, "Restart").
- The latest AC-16 deployed results are from `f2b607c` (`2026-10-18-deployed.md`). There are code changes between `f2b607c` and `f551649`: the course testing interface, migration 0002, coverage instrumentation, and max instances changed to 1. The incident and evidence routes are unchanged. CI's AC-16 smoke run on `f551649` passed (run 39182054445: 100/100, 200/200 within 1 s on loopback), but CI runs without `APP_COVERAGE`, so it says nothing about the instrumentation's cost when deployed.
```

### `docs/test-results/2026-10-18-cross-team-ours-on-theirs.md`

```markdown
# 2026-10-18: our acceptance suite against the other team's service

Owner: Mohit. **Target: the other team's deployment**, https://incident-clock.onrender.com. Their key was shared privately. It isn't recorded here.

## Conditions

| | |
| --- | --- |
| Date | 2026-10-18, about 8:30 PM local |
| Our suite | `tests/acceptance/` at `38972ff` (`integration`) |
| Their version | Not shared |
| Mode | Non-destructive: `ALLOW_DESTRUCTIVE_TESTS` was not set, because no reset window has been agreed |
| Client | A laptop over the public internet |

## Result

**45 passed, 0 failed, 3 skipped** (`pytest -m acceptance`).

- The 3 skips are the `/reset` tests in `test_system_endpoints.py`. They were skipped on purpose so we wouldn't wipe their data.
- All the AC-01 to AC-05 and AC-14 tests passed: create/retrieve, invalid input gives 400 naming the field, unknown IDs give 404, evidence attachment, 405 on edit/delete, missing/wrong key gives 401, HTTPS.
- Their `/health` returns `{"status":"ok"}`, lowercase. Ours returns `"OK"`. The contract only requires a string, so both pass.

## Not yet run

- The `/reset` tests and the AC-16 scripts (persistence, response time). Both reset the target, so they wait for an agreed window.
- Their tests against our service.

The run left some synthetic test incidents (titles and descriptions from `tests/fixtures/data/`) in their database.
```

### `docs/test-results/cross-team.md`

```markdown
# Cross-team testing (Q6)

Owner: Mohit. Both directions have to be attempted and recorded, including failures and who owns each issue.

## What we need from the other team

- [x] Their deployed HTTPS base URL: https://incident-clock.onrender.com (tester: https://incident-clock-tester.onrender.com).
- [x] A shared synthetic test API key, exchanged privately. Never put it in git, chat screenshots or the report.
- [ ] A written schedule for runs that call `POST /reset` or `/test/setup`. None exists yet. The 2026-10-18 tester runs happened without one.
- [ ] Their position on the open contract questions: `GET /incidents` (issue #2) and length limits (issue #3).

## What we give them

- Our deployed base URL, https://incident-api-356019173418.us-central1.run.app, and the test key (private channel only; see `docs/submission/q2-deployment.md`).
- The shared fixtures in `tests/fixtures/data/`, as plain JSON in the AC-01 format.
- The commands below. Our suite only needs Python 3.12 and `uv`.

## Running our suite against their service

```sh
export BASE_URL=https://<their-service> API_KEY=<their test key>
uv run pytest -m acceptance                       # non-destructive
ALLOW_DESTRUCTIVE_TESTS=1 uv run pytest -m acceptance    # only inside the agreed reset window
uv run python -m scripts.performance              # response time
```

Record each run in this folder with the date, their commit or version if they share it, totals, every failure (expected vs actual, plus a reproducible request), and whether the failure points to their implementation, ours, or the shared spec.

## Status

| Direction | Status |
| --- | --- |
| Our tests → their service | Non-destructive run 2026-10-18: [45 passed, 0 failed, 3 reset tests skipped](2026-10-18-cross-team-ours-on-theirs.md). Reset tests and AC-16 wait for an agreed window |
| Their tests → our service | **Pending.** Our system has `/test/setup` and `/test/report` (`f551649`). No report from their tester exists yet |
| Our tester → their service | Done 2026-10-18 by Srihari: **48 pass, 0 fail, 0 skipped**; code 325/406 (their basis), system 8/16. See `docs/cross-team-testing.md` |
```

## Part 10: Contract issues and the cross-team testing interface

### `docs/contract-issues.md`

```markdown
# Contract issues and open questions

Owner: Mohit. Record each decision, who agreed to it, and the date it was resolved.

Sources checked: the pod's common contract in *Phase 2 - Pod.pdf* and the user-supplied *Phase 2 - Pod.docx*: Q3.2 models, Q5.1 interface table, Q5.2 schemas, valid/invalid examples, and AC-01 to AC-16.

| # | Issue | Status | Decision |
| --- | --- | --- | --- |
| 1 | Obtain the instructor-provided OpenAPI spec, confirm its version, and check how it relates to the Phase 2 common contract. | Decided (team) | No instructor OpenAPI file could be found. Team decision (Astha, Mohit; 2026-10-16): build and test against the Phase 2 pod specification v1.0 (Q1.3; Q5 common JSON API). If an instructor OpenAPI file turns up, compare it with Q5 and record the differences here. |
| 2 | Phase 2 AC-02 mentions listing incidents, but the Phase 2 interface table omits `GET /incidents`. Does the route exist? | Confirmed conflict; proposal awaiting pod agreement | AC-02 uses listing; Q5.1 omits a list route. See [Issue 2](#issue-2-get-incidents) below. No extra endpoint added. |
| 3 | Agree exact field length limits (and the whitespace policy) for incident and evidence fields. | Open | Q5.2 explicitly leaves title/description maximum lengths to team agreement; no numeric limits are provided. Existing nonblank checks preserve submitted text. Integration now reuses shared provisional storage limits (title 200, description 5000, reporterName/source 500) so oversized inputs return 400; these numbers are not pod-approved and need coordinated config/schema/migration review. |
| 4 | Confirm error response formats, and the precedence between validation and authentication failures (e.g. invalid body with a missing API key). | Resolved by the spec | Q3.2 Model 4: authentication, endpoint/method, incident existence, body validation, workflow state. Q5 requires error/message JSON; REQ-02 and Model 4 require the bad field name for 400. Feature routes now use shared authentication/error infrastructure and check evidence parent existence before parsing the body. Real-app tests exercise authentication-first ordering with an injected repository; PostgreSQL execution remains unverified locally. Exact incident/evidence error codes are not enumerated. |

These are observations from the supplied specification, not newly negotiated pod
decisions. For Phase 3 only incident/evidence operations are implemented; Q6.1
retains database, auth, reset, deployment, and persistence verification obligations.

Model 2 uses internal `reported_by` while Q5 uses public `reporterName`; the shared ORM and API both use reporter_name, mapped to reporterName in JSON. `created_at` is internal and is absent
from Q5 incident retrieval JSON. Later-phase document discrepancies (including
2025 acceptance dates versus the Model 3 2026–2027 holiday list) need agreement
before deadline work; no deadline functionality is implemented here.

## Issue 2: GET /incidents

**Evidence (Phase 2 - Pod.pdf):**

- AC-02's action is "POST each one, then **list all incidents**". Its expected result says "the incident **count is unchanged**".
- AC-16's action is "Restart the service and **GET the incidents**". Its expected result says "All 100 incidents remain after the restart" and "**no incidents remain** after the reset".
- The Q5.1 interface table defines only `GET /health`, `POST /incidents`, `GET /incidents/{incidentId}` (and its sub-resources), and `POST /reset`. There is no collection `GET /incidents`.

Without a list route, neither AC-02's "count unchanged" check nor AC-16's "no incidents remain" check can be automated. This is a gap in a contract both teams share, so one team can't settle it alone.

**Proposed resolution (needs agreement from the pod and the other team):**

Add `GET /incidents` to the common contract:

- It requires `X-API-Key` and returns 401 otherwise.
- It returns `200 OK` with a JSON array of Incident objects, each with the same shape as `GET /incidents/{incidentId}`.
- After `POST /reset`, it returns an empty array.

That is the smallest addition that makes AC-02 and AC-16 testable as written. Ordering, pagination, and filters stay out of scope unless the pod asks for them.

**Fallback if the pod declines:** change AC-02 to check that each rejected POST returns 400 naming the bad field, without the count check. Change AC-16 to re-GET each of the 100 IDs it created before the restart, and confirm with 404s after the reset. Either way, the acceptance tests won't call `GET /incidents` until this row is marked agreed.

**Decision:** _pending. Record who agreed and the date._
```

### `docs/cross-team-testing.md`

```markdown
# Cross-team testing interface

Owner: Srihari. Implements the course's "Cross-team Testing Interface"
(student-facing spec): our **system** exposes `POST /test/setup` and
`GET /test/report`, and our **tester** is a separate service with
`POST /test/setup`, `POST /test/run` and `GET /test/report`.

## Registry values

| Field | Value |
| --- | --- |
| System base URL | https://incident-api-356019173418.us-central1.run.app |
| Tester base URL | https://incident-tester-356019173418.us-central1.run.app |
| Intra-pod spec | Phase 2 pod specification (common contract Q5.1–Q5.3, AC-01 to AC-16) |
| Access | Every system endpoint except `/health` needs the shared key in `X-API-Key`. The key is shared by private message only, never in the registry, repo or chat. The tester's endpoints are open; it only targets approved URLs. |

## Our system: `/test/setup`, `/test/report`

- `POST /test/setup {"session_id", "setup": {}}` → `201 {"session_id"}`.
  Resets the database to an empty baseline (no incidents, no evidence, IDs start
  at `INC-001` / `EVD-001`) and starts code coverage for the session. A session ID
  can be used once; reusing it is `409`. Takes well under a second.
- `GET /test/report?session_id=...` → `200 {"session_id", "coverage": {"code": ...}}`
  with the lines of the `app` package executed by project requests since that
  setup. Reading the report doesn't change the numbers. Unknown session: `404`.
- One session is active at a time: a new setup resets the data and starts a new
  measurement. Project requests carry no session ID. **Tell us before a run** so
  two teams don't reset the system at the same time.
- Errors on `/test/...` are `{"message", "source": "system"}` (plus `error` on 401).

## Our tester

- `POST /test/setup {"target_url"}` → `201 {"session_id"}` (a new UUID). It calls
  the target's `/test/setup` with that ID. The target URL must be an approved pod
  system URL (no query, no `/test` suffix); anything else is `400`. If the system's
  setup fails, its status, message and source are passed back unchanged; if the
  system can't be reached, `500` with `source: communication`.
- `POST /test/run {"session_id"}` → `200` with the full report when the suite
  finishes. A session runs once; running it again is `409`. If the run aborts
  (time limit, crash), `500` and the report keeps the results so far: the test in
  progress is `error` (source `tester`), the rest `skip`.
- `GET /test/report?session_id=...` → the stored report; `409` before the run.
- What it runs: our acceptance suite, `tests/acceptance` (48 tests,
  destructive tests included). Outcomes are `pass`, `fail`, `error` (source
  `system` for 5xx answers, `communication` for timeouts/connection errors, `tester`
  for our own failures) and `skip`.
- Coverage in the report:
  - **code:** taken from the target's `/test/report`
  - **component:** null, because the pod spec defines no component list
  - **system:** acceptance criteria exercised, out of AC-01 to AC-16
- Time limits: setup 60 s, run 600 s (Cloud Run request timeout 900 s).

## Adding the other team's system

Their key goes in Secret Manager, never in the repo:

```sh
printf '%s' '{"<their base url>": "<their key>"}' | \
  gcloud secrets create tester-target-keys --data-file=- --project ece30861-project-62ca4b
PROJECT_ID=ece30861-project-62ca4b \
ALLOWED_TARGETS=https://incident-api-356019173418.us-central1.run.app,<their base url> \
  scripts/deploy_tester_gcp.sh
```

(Use `gcloud secrets versions add` if the secret already exists.) Targets with
no entry there use our own `api-key`.

## Running it

```sh
T=https://incident-tester-356019173418.us-central1.run.app
curl -s -X POST $T/test/setup -H 'Content-Type: application/json' \
  -d '{"target_url": "https://incident-api-356019173418.us-central1.run.app"}'
curl -s -X POST $T/test/run -H 'Content-Type: application/json' -d '{"session_id": "<id>"}'
curl -s "$T/test/report?session_id=<id>"
```

## Live check (2026-10-18, commit `f551649`)

Our tester against our deployed system:

- Setup: `201` in 0.8 s.
- Report before the run: `409`.
- Run: `200` in 5.9 s. **48 pass** with unique test IDs. Coverage: code 135/522
  lines, component null with a reason, system 8/16 (AC-01, 02, 03, 04, 05, 08, 14, 16).
  "System" counts ACs with at least one test run, not ACs fully met: AC-08 is
  only its REQ-07 edit/delete half, and AC-16 is only the reset tests.
- Running again: `409`. The stored report matches the run response.
- Non-approved target: `400`.
- Our system's `/test/setup` without a key: `401` with `source: system`.

## Cross-team run: our tester against the other team's system (2026-10-18)

Target: https://incident-clock.onrender.com, key stored in Secret Manager
(`tester-target-keys`). Session `7c8dd57b-c179-48f1-8a92-465b4d8063be`.

- Setup: `201` in 0.8 s. Run: `200` in 9.9 s. **48 pass**, nothing failed or skipped.
  The stored report matches the run response.
- Coverage:
  - code: 325/406 lines, reported by their system; their basis counts lines run at import as executed, ours doesn't, so the two numbers can't be compared directly
  - component: null
  - system: 8/16
```

## Part 11: CI workflow source

### `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, integration]
  pull_request:

permissions:
  contents: read

jobs:
  checks:
    runs-on: ubuntu-latest

    # Disposable database for the infrastructure DB tests and the in-CI app.
    # Both reset it; it never holds real data.
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: ci
          POSTGRES_PASSWORD: ci-only
          POSTGRES_DB: ci
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U ci -d ci"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10

    env:
      TEST_DATABASE_URL: postgresql+psycopg://ci:ci-only@127.0.0.1:5432/ci

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6
        with:
          version: "0.9.28"

      - name: Install Python 3.12
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --locked

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: mypy
        run: uv run mypy

      - name: pytest (unit, infrastructure, client self-tests)
        run: uv run pytest -m "not acceptance"

      # Black-box acceptance tests against the app served locally in CI. Uses a
      # throwaway key; deployed-service runs are done separately, not from CI.
      - name: Start app for acceptance tests
        env:
          DATABASE_URL: ${{ env.TEST_DATABASE_URL }}
          API_KEY: ci-acceptance-key
        run: |
          uv run alembic upgrade head
          nohup .venv/bin/uvicorn app.main:app --port 8000 > app.log 2>&1 &
          for i in $(seq 30); do curl -sf http://127.0.0.1:8000/health && exit 0; sleep 1; done
          cat app.log; exit 1

      - name: pytest (acceptance, local app)
        env:
          BASE_URL: http://127.0.0.1:8000
          API_KEY: ci-acceptance-key
          # Safe here: the target is the throwaway app and database inside this job.
          ALLOW_DESTRUCTIVE_TESTS: "1"
        run: uv run pytest -m acceptance

      # AC-16 smoke run against the in-job app: restart persistence, reset, and
      # response time. Real results come from runs against the deployment.
      - name: AC-16 persistence across an app restart
        env:
          DATABASE_URL: ${{ env.TEST_DATABASE_URL }}
          BASE_URL: http://127.0.0.1:8000
          API_KEY: ci-acceptance-key
          ALLOW_DESTRUCTIVE_TESTS: "1"
        run: |
          uv run python -m scripts.check_persistence create --state ci-run.json
          pkill -f "uvicorn app.main:app"
          sleep 1
          nohup .venv/bin/uvicorn app.main:app --port 8000 >> app.log 2>&1 &
          for i in $(seq 30); do curl -sf "$BASE_URL/health" >/dev/null && break; sleep 1; done
          uv run python -m scripts.check_persistence verify --state ci-run.json
          uv run python -m scripts.check_persistence reset --state ci-run.json

      - name: AC-16 response time
        env:
          BASE_URL: http://127.0.0.1:8000
          API_KEY: ci-acceptance-key
        run: uv run python -m scripts.performance

      - name: App log
        if: always()
        run: cat app.log || true

      # Stop the background server so nothing holds uv's cache lock during cleanup.
      - name: Stop app
        if: always()
        run: pkill -f "uvicorn app.main:app" || true
```

## Part 12: Acceptance suite source (the test files)

### `tests/acceptance/assertions.py`

```python
"""Shared assertions for acceptance tests, written from the pod contract (Q5)."""

from datetime import datetime, timedelta

import httpx


def assert_error_body(response: httpx.Response, status: int) -> dict[str, str]:
    """Contract: every error is {"error": "ERROR_CODE", "message": "..."}."""
    assert response.status_code == status, response.text
    body: dict[str, str] = response.json()
    assert isinstance(body.get("error"), str) and body["error"], body
    assert isinstance(body.get("message"), str) and body["message"], body
    return body


def _squash(text: str) -> str:
    return text.replace("_", "").replace(" ", "").lower()


def assert_names_field(body: dict[str, str], field: str) -> None:
    """REQ-02/AC-02: a 400 names the bad field (in the code or the message, any case)."""
    haystack = _squash(body["error"] + body["message"])
    assert _squash(field) in haystack, f"error does not name {field!r}: {body}"


def assert_utc_instant(actual: str, expected: str) -> None:
    """Contract: response timestamps are UTC and keep the submitted instant."""
    parsed = datetime.fromisoformat(actual)
    assert parsed.utcoffset() == timedelta(0), f"{actual} is not UTC"
    assert parsed == datetime.fromisoformat(expected), f"{actual} != {expected}"
```

### `tests/acceptance/test_ac14_security.py`

```python
"""AC-14: public health, API-key enforcement, and HTTPS deployment.

Assumption (docs/contract-issues.md #4): authentication is checked before the
resource lookup, so an unknown incident ID without a valid key returns 401.
Error body format is not asserted until the contract defines it.
"""

import pytest

from tests.acceptance.client import ApiClient, Auth

pytestmark = pytest.mark.acceptance

# Synthetic ID that no service should contain; used only to reach an authenticated route.
UNKNOWN_INCIDENT_PATH = "/incidents/acceptance-unknown-id-000"


def test_health_is_public(api: ApiClient) -> None:
    response = api.get("/health", auth=Auth.MISSING)
    assert response.status_code == 200


@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG], ids=["missing-key", "wrong-key"])
def test_authenticated_route_rejects_bad_key(api: ApiClient, auth: Auth) -> None:
    response = api.get(UNKNOWN_INCIDENT_PATH, auth=auth)
    assert response.status_code == 401


def test_authenticated_route_accepts_valid_key(api: ApiClient, require_api_key: None) -> None:
    response = api.get(UNKNOWN_INCIDENT_PATH)
    assert response.status_code != 401


def test_deployment_uses_https(api: ApiClient) -> None:
    if api.config.is_local:
        pytest.skip("local target; HTTPS is only required for the deployment")
    assert api.config.is_https, f"deployed BASE_URL must use https: {api.config.base_url}"
```

### `tests/acceptance/test_system_endpoints.py`

```python
"""Black-box checks of the system endpoints and the shared error format.

Covers REQ-14 reset (AC-16, reset part), AC-03's GET half, and AC-14's error
bodies. Reset tests are destructive and only run with ALLOW_DESTRUCTIVE_TESTS=1.
"""

import pytest

from tests.acceptance.assertions import assert_error_body
from tests.acceptance.client import ApiClient, Auth
from tests.fixtures.data import unknown_incident_ids

pytestmark = pytest.mark.acceptance


def test_health_body_has_status(api: ApiClient) -> None:
    response = api.get("/health", auth=Auth.MISSING)
    assert response.status_code == 200
    assert isinstance(response.json().get("status"), str)


@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG], ids=["missing-key", "wrong-key"])
def test_401_uses_error_format(api: ApiClient, auth: Auth) -> None:
    assert_error_body(api.get("/incidents/INC-999999", auth=auth), 401)


@pytest.mark.parametrize("incident_id", unknown_incident_ids())
def test_unknown_incident_get_is_404_with_error_format(
    api: ApiClient, require_api_key: None, incident_id: str
) -> None:
    assert_error_body(api.get(f"/incidents/{incident_id}"), 404)


@pytest.mark.parametrize("auth", [Auth.MISSING, Auth.WRONG], ids=["missing-key", "wrong-key"])
def test_reset_requires_key(api: ApiClient, allow_destructive: None, auth: Auth) -> None:
    # Destructive-gated: if auth were broken, this request would wipe the target.
    assert_error_body(api.post("/reset", auth=auth), 401)


def test_reset_succeeds_and_is_repeatable(api: ApiClient, reset_service: None) -> None:
    # reset_service has already reset once; a second reset on empty data must also work.
    response = api.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"status": "RESET_COMPLETE"}
```

### `tests/acceptance/test_ac01_05_incidents_evidence.py`

```python
"""AC-01 to AC-05: incident create/retrieve, rejection, unknown IDs, evidence.

Driven by the shared JSON fixtures in tests/fixtures/data/. Writes synthetic
incidents to the target but never resets it, so these are not destructive.

AC-02's "incident count is unchanged" needs a list route (docs/contract-issues.md
#2). Until then, rejected evidence is checked by re-reading the parent incident.
"""

from typing import Any

import pytest

from tests.acceptance.assertions import assert_error_body, assert_names_field, assert_utc_instant
from tests.acceptance.client import ApiClient
from tests.fixtures.data import (
    INVALID_EVIDENCE,
    INVALID_INCIDENTS,
    VALID_EVIDENCE,
    VALID_INCIDENTS,
    Case,
    unknown_incident_ids,
)

pytestmark = [pytest.mark.acceptance, pytest.mark.usefixtures("require_api_key")]

INCIDENT_TEXT_FIELDS = ("title", "description", "reporterName")
EVIDENCE_TEXT_FIELDS = ("category", "summary", "source")


def _ids(cases: list[Case]) -> list[str]:
    return [c.name for c in cases]


def _evidence(name: str) -> Case:
    return next(c for c in VALID_EVIDENCE if c.name == name)


def create_incident(api: ApiClient, case: Case = VALID_INCIDENTS[0]) -> str:
    response = api.post("/incidents", json=case.body)
    assert response.status_code == 201, response.text
    body = response.json()
    assert isinstance(body.get("incidentId"), str) and body["incidentId"]
    assert body.get("status") == "OPEN"
    return str(body["incidentId"])


def get_incident(api: ApiClient, incident_id: str) -> dict[str, Any]:
    response = api.get(f"/incidents/{incident_id}")
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


def attach(api: ApiClient, incident_id: str, case: Case) -> dict[str, Any]:
    response = api.post(f"/incidents/{incident_id}/evidence", json=case.body)
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    assert isinstance(body.get("evidenceId"), str) and body["evidenceId"]
    assert isinstance(body.get("recordedAt"), str)
    assert_utc_instant(body["recordedAt"], body["recordedAt"])
    return body


def assert_evidence_matches(stored: dict[str, Any], case: Case, created: dict[str, Any]) -> None:
    assert stored["evidenceId"] == created["evidenceId"]
    for field in EVIDENCE_TEXT_FIELDS:
        assert stored[field] == case.body[field], field
    assert_utc_instant(stored["collectedAt"], case.expected["collectedAt"])
    assert_utc_instant(stored["recordedAt"], created["recordedAt"])


# AC-01 ---------------------------------------------------------------------


@pytest.mark.parametrize("case", VALID_INCIDENTS, ids=_ids(VALID_INCIDENTS))
def test_ac01_create_then_retrieve_returns_identical_values(api: ApiClient, case: Case) -> None:
    incident_id = create_incident(api, case)

    body = get_incident(api, incident_id)

    assert body["incidentId"] == incident_id
    for field in INCIDENT_TEXT_FIELDS:
        assert body[field] == case.body[field], field
    assert_utc_instant(body["discoveredAt"], case.expected["discoveredAt"])
    assert body["status"] == case.expected["status"]
    assert body["evidence"] == []
    assert body["currentDecision"] is None
    assert body["filing"] is None


def test_ac01_each_incident_gets_a_distinct_id(api: ApiClient) -> None:
    assert create_incident(api) != create_incident(api)


# AC-02 ---------------------------------------------------------------------


@pytest.mark.parametrize("case", INVALID_INCIDENTS, ids=_ids(INVALID_INCIDENTS))
def test_ac02_invalid_incident_is_rejected_naming_the_field(api: ApiClient, case: Case) -> None:
    body = assert_error_body(api.post("/incidents", json=case.body), 400)
    assert_names_field(body, case.expected["field"])


# AC-03 ---------------------------------------------------------------------


@pytest.mark.parametrize("incident_id", unknown_incident_ids())
def test_ac03_unknown_id_get_and_post_return_404(api: ApiClient, incident_id: str) -> None:
    assert_error_body(api.get(f"/incidents/{incident_id}"), 404)
    response = api.post(f"/incidents/{incident_id}/evidence", json=VALID_EVIDENCE[0].body)
    assert_error_body(response, 404)


# AC-04 ---------------------------------------------------------------------


def test_ac04_three_technical_items_are_linked_to_the_incident(api: ApiClient) -> None:
    incident_id = create_incident(api)
    cases = [_evidence(f"ac04-technical-{n}") for n in (1, 2, 3)]
    created = [attach(api, incident_id, case) for case in cases]
    assert len({c["evidenceId"] for c in created}) == 3

    stored = {e["evidenceId"]: e for e in get_incident(api, incident_id)["evidence"]}

    assert set(stored) == {c["evidenceId"] for c in created}
    for case, made in zip(cases, created, strict=True):
        assert_evidence_matches(stored[made["evidenceId"]], case, made)

    unknown = unknown_incident_ids()[0]
    assert_error_body(api.post(f"/incidents/{unknown}/evidence", json=cases[0].body), 404)


def test_ac04_evidence_is_not_shared_between_incidents(api: ApiClient) -> None:
    first, second = create_incident(api), create_incident(api)
    attach(api, first, _evidence("ac04-technical-1"))

    assert get_incident(api, second)["evidence"] == []


# AC-05 and the other categories --------------------------------------------


@pytest.mark.parametrize("case", VALID_EVIDENCE, ids=_ids(VALID_EVIDENCE))
def test_ac05_evidence_is_stored_and_returned_unchanged(api: ApiClient, case: Case) -> None:
    incident_id = create_incident(api)
    created = attach(api, incident_id, case)

    (stored,) = get_incident(api, incident_id)["evidence"]

    assert_evidence_matches(stored, case, created)


@pytest.mark.parametrize("case", INVALID_EVIDENCE, ids=_ids(INVALID_EVIDENCE))
def test_invalid_evidence_is_rejected_and_not_attached(api: ApiClient, case: Case) -> None:
    incident_id = create_incident(api)

    body = assert_error_body(api.post(f"/incidents/{incident_id}/evidence", json=case.body), 400)

    assert_names_field(body, case.expected["field"])
    assert get_incident(api, incident_id)["evidence"] == []


# Append-only (contract Q5.1: edit/delete attempts return 405) --------------


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_stored_incident_cannot_be_edited_or_deleted(api: ApiClient, method: str) -> None:
    incident_id = create_incident(api)

    assert_error_body(api.request(method, f"/incidents/{incident_id}", json={}), 405)

    assert get_incident(api, incident_id)["title"] == VALID_INCIDENTS[0].body["title"]
```

## Part 13: AC-16 scripts (usage)

### `scripts/README.md`

```markdown
# Scripts

Both scripts read `BASE_URL` and `API_KEY` from the environment. Never hardcode deployed URLs or credentials. Anything that calls `POST /reset` also requires `ALLOW_DESTRUCTIVE_TESTS=1`. Only point those at the agreed synthetic test service, and agree a time with the other team first.

| Script | Owner | Purpose |
| --- | --- | --- |
| `start.sh` | Srihari | Container entry point: migrate, then serve |
| `performance.py` | Mohit | AC-16 response time: loads 100 incidents, times 200 sequential requests, passes if at least 95% finish within 1 s. Prints the test conditions with the result |
| `check_persistence.py` | Mohit | AC-16 restart persistence and reset, in three steps: `create`, restart the service yourself, `verify`, then (destructive) `reset` |
| `common.py` | Mohit | Shared client, fixture loading and run conditions |

```sh
export BASE_URL=https://<deployment> API_KEY=<shared test key>

uv run python -m scripts.check_persistence create --state run.json
# restart the service WITHOUT /reset (locally: docker compose restart app)
uv run python -m scripts.check_persistence verify --state run.json

uv run python -m scripts.performance --json-out perf.json

ALLOW_DESTRUCTIVE_TESTS=1 uv run python -m scripts.check_persistence reset --state run.json
```

Exit codes: 0 means pass, 1 means fail, 2 means the script couldn't run (bad configuration, or setup requests failed). Record each real run in `docs/test-results/`.
```

## Part 14: Shared fixtures

### `tests/fixtures/README.md`

```markdown
# Test fixtures

Owner: Mohit.

Synthetic data for the acceptance tests. The JSON files in `data/` are plain JSON, so we can share them with the other team (Phase 2, Q4.2) without them needing our code:

| File | Contents |
| --- | --- |
| `data/incidents_valid.json` | Valid `POST /incidents` bodies (AC-01), each with the expected `status` and the UTC-normalized `discoveredAt` |
| `data/incidents_invalid.json` | Bodies that must be rejected with 400 naming `expected.field`. Includes AC-02's three cases |
| `data/evidence_valid.json` | One evidence item per category, including AC-04's three TECHNICAL items and AC-05's BUSINESS_IMPACT item |
| `data/evidence_invalid.json` | Evidence bodies that must be rejected with 400 |
| `data/unknown_ids.json` | Incident IDs the tests never create (AC-03) |

Each case has the shape `{"name", "body", "expected"}`. `data.py` loads the files, and `test_fixture_data.py` checks them against the contract's field rules in CI.

Not included yet: maximum-length boundary cases. They're waiting on the agreed limits (`docs/contract-issues.md` #3).

Use synthetic data only. No real incident data and no credentials.
```

### `tests/fixtures/data/evidence_invalid.json`

```json
{
  "description": "Invalid evidence bodies for an existing incident. Each must return 400 naming expected.field and must not attach evidence.",
  "cases": [
    {
      "name": "unknown-category",
      "body": {"category": "PROBABLY_TECHNICAL", "summary": "Bad category.", "source": "EDR", "collectedAt": "2025-03-14T10:00:00Z"},
      "expected": {"httpStatus": 400, "field": "category"}
    },
    {
      "name": "lowercase-category",
      "body": {"category": "technical", "summary": "Categories are upper case.", "source": "EDR", "collectedAt": "2025-03-14T10:00:00Z"},
      "expected": {"httpStatus": 400, "field": "category"}
    },
    {
      "name": "missing-category",
      "body": {"summary": "No category.", "source": "EDR", "collectedAt": "2025-03-14T10:00:00Z"},
      "expected": {"httpStatus": 400, "field": "category"}
    },
    {
      "name": "empty-summary",
      "body": {"category": "TECHNICAL", "summary": "", "source": "EDR", "collectedAt": "2025-03-14T10:00:00Z"},
      "expected": {"httpStatus": 400, "field": "summary"}
    },
    {
      "name": "missing-source",
      "body": {"category": "TECHNICAL", "summary": "No source.", "collectedAt": "2025-03-14T10:00:00Z"},
      "expected": {"httpStatus": 400, "field": "source"}
    },
    {
      "name": "collected-at-without-offset",
      "body": {"category": "TECHNICAL", "summary": "No offset.", "source": "EDR", "collectedAt": "2025-03-14T10:00:00"},
      "expected": {"httpStatus": 400, "field": "collectedAt"}
    },
    {
      "name": "missing-collected-at",
      "body": {"category": "TECHNICAL", "summary": "No timestamp.", "source": "EDR"},
      "expected": {"httpStatus": 400, "field": "collectedAt"}
    }
  ]
}
```

### `tests/fixtures/data/evidence_valid.json`

```json
{
  "description": "Valid POST /incidents/{incidentId}/evidence bodies (AC-04, AC-05). expected.collectedAt is the same instant in UTC. The contract puts no future-time limit on collectedAt.",
  "cases": [
    {
      "name": "contract-example-business-impact",
      "body": {"category": "BUSINESS_IMPACT", "summary": "Order processing was unavailable for three hours.", "source": "Operations report", "collectedAt": "2026-09-21T17:30:00-04:00"},
      "expected": {"collectedAt": "2026-09-21T21:30:00Z"}
    },
    {
      "name": "ac04-technical-1",
      "body": {"category": "TECHNICAL", "summary": "EDR flagged mass file encryption on db-01.", "source": "EDR console", "collectedAt": "2025-03-14T10:00:00Z"},
      "expected": {"collectedAt": "2025-03-14T10:00:00Z"}
    },
    {
      "name": "ac04-technical-2",
      "body": {"category": "TECHNICAL", "summary": "Ransom note found in shared drive root.", "source": "File server audit log", "collectedAt": "2025-03-14T10:20:00-05:00"},
      "expected": {"collectedAt": "2025-03-14T15:20:00Z"}
    },
    {
      "name": "ac04-technical-3",
      "body": {"category": "TECHNICAL", "summary": "Outbound connections to a known C2 address.", "source": "Firewall logs", "collectedAt": "2025-03-14T11:45:30+01:00"},
      "expected": {"collectedAt": "2025-03-14T10:45:30Z"}
    },
    {
      "name": "legal",
      "body": {"category": "LEGAL", "summary": "Outside counsel notified of possible disclosure obligations.", "source": "Legal department memo", "collectedAt": "2025-03-15T09:00:00Z"},
      "expected": {"collectedAt": "2025-03-15T09:00:00Z"}
    },
    {
      "name": "other",
      "body": {"category": "OTHER", "summary": "Press inquiry received about the outage.", "source": "Communications team", "collectedAt": "2025-03-15T13:00:00Z"},
      "expected": {"collectedAt": "2025-03-15T13:00:00Z"}
    }
  ]
}
```

### `tests/fixtures/data/incidents_invalid.json`

```json
{
  "description": "Invalid POST /incidents bodies. Each must return 400 naming expected.field, and must not create an incident (AC-02). The first three are AC-02's listed cases. Length-limit cases wait for docs/contract-issues.md #3.",
  "cases": [
    {
      "name": "ac02-missing-description",
      "body": {"title": "Missing description", "discoveredAt": "2025-03-14T09:30:00Z", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "description"}
    },
    {
      "name": "ac02-timestamp-without-offset",
      "body": {"title": "No offset", "description": "Timestamp lacks a timezone offset.", "discoveredAt": "2025-03-14T09:30:00", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "discoveredAt"}
    },
    {
      "name": "ac02-future-discovery",
      "body": {"title": "Future discovery", "description": "Discovered in the future.", "discoveredAt": "2099-01-01T00:00:00Z", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "discoveredAt"}
    },
    {
      "name": "missing-title",
      "body": {"description": "No title.", "discoveredAt": "2025-03-14T09:30:00Z", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "title"}
    },
    {
      "name": "missing-discovered-at",
      "body": {"title": "No timestamp", "description": "No discoveredAt.", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "discoveredAt"}
    },
    {
      "name": "missing-reporter-name",
      "body": {"title": "No reporter", "description": "No reporterName.", "discoveredAt": "2025-03-14T09:30:00Z"},
      "expected": {"httpStatus": 400, "field": "reporterName"}
    },
    {
      "name": "empty-title",
      "body": {"title": "", "description": "Empty title.", "discoveredAt": "2025-03-14T09:30:00Z", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "title"}
    },
    {
      "name": "empty-reporter-name",
      "body": {"title": "Empty reporter", "description": "Empty reporterName.", "discoveredAt": "2025-03-14T09:30:00Z", "reporterName": ""},
      "expected": {"httpStatus": 400, "field": "reporterName"}
    },
    {
      "name": "malformed-timestamp",
      "body": {"title": "Bad timestamp", "description": "Not a date.", "discoveredAt": "yesterday", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "discoveredAt"}
    },
    {
      "name": "title-wrong-type",
      "body": {"title": 12345, "description": "Title is a number.", "discoveredAt": "2025-03-14T09:30:00Z", "reporterName": "SOC"},
      "expected": {"httpStatus": 400, "field": "title"}
    }
  ]
}
```

### `tests/fixtures/data/incidents_valid.json`

```json
{
  "description": "Valid POST /incidents bodies (AC-01). expected.discoveredAt is the same instant in UTC, as GET /incidents/{incidentId} must return it.",
  "cases": [
    {
      "name": "contract-example-ransomware",
      "body": {
        "title": "Order system ransomware",
        "description": "Encryption detected on production servers.",
        "discoveredAt": "2026-09-21T14:30:00-04:00",
        "reporterName": "Security Operations"
      },
      "expected": {"status": "OPEN", "discoveredAt": "2026-09-21T18:30:00Z"}
    },
    {
      "name": "utc-z-suffix",
      "body": {
        "title": "Phishing campaign against finance team",
        "description": "Several employees reported credential-harvesting emails.",
        "discoveredAt": "2025-03-14T09:30:00Z",
        "reporterName": "Help Desk"
      },
      "expected": {"status": "OPEN", "discoveredAt": "2025-03-14T09:30:00Z"}
    },
    {
      "name": "positive-half-hour-offset",
      "body": {
        "title": "Unauthorized VPN login",
        "description": "Successful VPN login from an unrecognized country.",
        "discoveredAt": "2025-11-02T08:15:00+05:30",
        "reporterName": "Network Monitoring"
      },
      "expected": {"status": "OPEN", "discoveredAt": "2025-11-02T02:45:00Z"}
    },
    {
      "name": "non-ascii-text",
      "body": {
        "title": "Exfiltración de datos — servidor de RR. HH.",
        "description": "Transferencia saliente inusual detectada (≈ 4 GB).",
        "discoveredAt": "2024-07-01T23:59:59-07:00",
        "reporterName": "Équipe SOC"
      },
      "expected": {"status": "OPEN", "discoveredAt": "2024-07-02T06:59:59Z"}
    }
  ]
}
```

### `tests/fixtures/data/unknown_ids.json`

```json
{
  "description": "Incident IDs the tests never create (AC-03): one in the contract's example format, and one in a format no service should generate.",
  "incidentIds": ["INC-999999", "does-not-exist-000"]
}
```

## Part 15: The other team's published contract (excerpt)

Fetched by Mohit on 2026-10-18 from `https://incident-clock.onrender.com/openapi.yaml` (433 lines; the key isn't reproduced). There's no `GET /incidents` and no `/test/*`, and title/description have `minLength: 1` with the max left open.

```yaml
openapi: 3.1.0
info:
  title: IncidentClock common interface contract
  version: 1.0.0
  description: >
    Machine-readable transcription of the pod's Phase 2 common interface contract
    (Phase 2 report, Sections 5.1 and 5.2, specification v1.0). This file adds no
    operations, fields, or behaviors beyond that submission. Where the submission
    leaves a value open (e.g. maximum string lengths), the schema leaves it open
    too; see docs/spec-issues.md.

    Behavior rules (Section 5.1): all resources are append-only; edit/delete requests
    return 405. A new incident starts OPEN. Evidence may be added in any status.
    Materiality is always entered by a human reviewer. MATERIAL moves the incident to
    MATERIAL_PENDING_FILING and creates a four-business-day deadline. A filing may only
    be recorded while MATERIAL_PENDING_FILING; afterwards the incident is FILED.
    State-invalid operations return 409 and change nothing. Request timestamps are
    RFC 3339 with an offset; response timestamps are UTC; dates are YYYY-MM-DD.

security:
  - ApiKey: []


paths:  # operations only
  /health:
    get:
      summary: Checks that the service is running.
  /incidents:
    post:
      summary: Creates a new cybersecurity incident.
  /incidents/{incidentId}:
    get:
      summary: Gets the current information for an incident.
  /incidents/{incidentId}/evidence:
    post:
      summary: Adds evidence to an existing incident.
  /incidents/{incidentId}/decisions:
    post:
      summary: Records a human materiality decision supported by evidence.
  /incidents/{incidentId}/corrections:
    post:
      summary: Replaces the current decision while preserving the previous decision in history.
  /incidents/{incidentId}/deadline-status:
    get:
      summary: Gets the current deadline status.
  /incidents/{incidentId}/filing:
    post:
      summary: Records an 8-K filing for a material incident.
  /incidents/{incidentId}/timeline:
    get:
      summary: Gets the incident timeline and evidence summary.
  /reset:
    post:
      summary: Clears all stored test data so automated tests can start from a known state.

components:
  schemas:  # selected
    Error:
      type: object
      required: [error, message]
      properties:
        error: {type: string, description: Error code}
        message: {type: string}

    IncidentCreate:
      type: object
      required: [title, description, discoveredAt, reporterName]
      properties:
        title: {type: string, minLength: 1, description: 'Max length agreed by both teams (open).'}
        description: {type: string, minLength: 1, description: 'Max length agreed by both teams (open).'}
        discoveredAt: {type: string, format: date-time, description: RFC 3339 with offset; not in the future.}
        reporterName: {type: string, minLength: 1}

    EvidenceCreate:
      type: object
      required: [category, summary, source, collectedAt]
      properties:
        category: {$ref: '#/components/schemas/EvidenceCategory'}
        summary: {type: string, minLength: 1}
        source: {type: string, minLength: 1}
        collectedAt: {type: string, format: date-time}

    Incident:
      type: object
      required: [incidentId, title, description, discoveredAt, reporterName, status, evidence, currentDecision, filing]
      properties:
        incidentId: {type: string}
        title: {type: string}
        description: {type: string}
        discoveredAt: {$ref: '#/components/schemas/UtcDateTime'}
        reporterName: {type: string}
        status: {$ref: '#/components/schemas/IncidentStatus'}
        evidence: {type: array, items: {$ref: '#/components/schemas/Evidence'}}
        currentDecision:
          oneOf: [{$ref: '#/components/schemas/Decision'}, {type: 'null'}]
        filing:
          oneOf: [{$ref: '#/components/schemas/Filing'}, {type: 'null'}]
```

---

End of evidence pack. Anything not recorded above hasn't been observed and shouldn't be claimed.
