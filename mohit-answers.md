# mohit-answers: evidence pack for Q4, Q6 and Q7

Owner: Mohit (acceptance testing, CI, performance and persistence verification, cross-team testing).
Project: ECE 30861 Phase 3, a cybersecurity incident and evidence API for the SEC disclosure rules.
Repository: https://github.com/asthap66/sec-project-ece30861, branch `integration`.
Compiled: 2026-10-18 (US Eastern evening; 2026-10-19 UTC).

## How to use this file

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
- Part 8: Submission drafts as committed (Q2, Q3, Q4, Q6, Q7)
- Part 9: Test-result records as committed
- Part 10: Contract issues and the cross-team testing interface
- Part 11: CI workflow source
- Part 12: Acceptance suite source (the test files)
- Part 13: AC-16 scripts (usage)
- Part 14: Shared fixtures (JSON)
- Part 15: The other team's published contract (`/openapi.yaml`, excerpt)

---

## Part 0: Facts at a glance

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
| Our system | https://incident-api-356019173418.us-central1.run.app | Google Cloud Run + Cloud SQL PostgreSQL 16, HTTPS, `X-App-Commit` header shows the deployed commit (`f551649` at compile time) |
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
| Acceptance suite | Our deployment (`ed5f449`) | Srihari, using Mohit's suite | **48 passed, 0 failed, 0 skipped** |
| Acceptance suite via our tester | Our deployment (`f551649`) | Srihari, through the deployed tester | **48 pass**; code coverage 135/522 lines; 8/16 ACs exercised |
| Restart persistence (AC-16) | Our deployment (`f2b607c`, same API) | Srihari, using Mohit's script | **100/100 incidents intact** after a Cloud Run revision restart; all removed by reset |
| Response time (AC-16) | Our deployment (`f2b607c`) | Srihari, using Mohit's script | **200/200 within 1 s** (target 95%); p50 48 ms, p95 61 ms, max 76 ms; 0 errors |
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
| AC-16 restart persistence; reset leaves nothing | `scripts/check_persistence.py create / verify / reset` |
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
| 2026-10-18 | Our deployment (`f2b607c`, same API) | — | **100/100** after revision `incident-api-00002-msv` → `incident-api-00003-ggj`; reset removed all 100 | **200/200 ≤ 1 s**; p50 48 ms, p95 61 ms, max 76 ms; 0 errors | Srihari, Mohit's scripts |
| 2026-10-18 | Our deployment (`f551649`) via our tester | **48 pass**; code coverage 135/522 lines; 8/16 ACs (AC-01, 02, 03, 04, 05, 08, 14, 16) | — | — | Srihari |
| 2026-10-18 | Other team's deployment | **45 passed, 0 failed, 3 skipped** (reset tests, on purpose) | not run | not run | Mohit |

**Evidence that the tests detect real failures.** This is the "failure explanations" part of Q4.
- **Mutation-style check.** Against a build of the app *without* Astha's incident and evidence routes, 33 of the 35 AC-01 to AC-05 tests failed. The 2 that still passed are unknown-ID 404 checks, which a missing route also satisfies by returning 404.
- **AC-14 checks.** Before the real service existed, the AC-14 tests passed against a throwaway local stub that checked keys, and failed against the bare scaffold that had no routes.
- **Real failures seen and explained.**
  1. *CI failure on PR #6.* The setup-uv post-job cache prune timed out because a background `uv run uvicorn` held the uv cache lock. The fix launches the app with `.venv/bin/uvicorn` and adds an always-run "Stop app" step. The next run passed.
  2. *Local failure of `tests/infrastructure/test_feature_database.py::test_postgres_create_retrieve_evidence_restart_reset`* (Astha's test, line 44: `assert before <= recorded <= datetime.now(UTC)`). The cause is clock skew: the Docker Desktop VM's clock (which sets PostgreSQL `now()`) differed from the host clock by about 3–4 s (host `date -u` 21:10:30 vs container 21:10:27; the assertion showed DB 21:10:21 vs host 21:10:17). It's not a code defect, and it passes in CI. The fix is a small tolerance.
  3. *One client-side timeout* (10 s) during the first deployed persistence run. Cloud Run's request logs showed no request slower than 0.36 s, so the network path is the likely cause. The run was repeated and passed.
  4. *Static-check failures during development*, all fixed before merge: a mypy `no-any-return` in `assertions.py`, Ruff E501 long lines in the scripts, and a Ruff import-order issue in `conftest.py`.

**Gaps (honest limits of the validation).**
- AC-02's count check and AC-16's "no incidents remain" need a list route (`GET /incidents`), which the pod contract doesn't have (contract issue #2). Both are checked one ID at a time instead.
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
| Suite design | Parts 12–14 (source of the HTTP client and scripts is in the repo: `tests/acceptance/client.py`, `scripts/*.py`) |

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
| Their tester → our system | Our system has the course interface (`/test/setup`, `/test/report`, Srihari, `f551649`). We sent our system and tester URLs; Srihari sends the key privately | **Not run yet** at compile time |
| Our tester → their system | Needs their key in our Secret Manager (`tester-target-keys`) and their URL in the tester's `ALLOWED_TARGETS` | **Not run yet** |
| Our tester → our system (check of our own interface) | 2026-10-18, Srihari | 48 pass; code coverage 135/522 lines; component coverage null (pod spec defines no components); system coverage 8/16 ACs |

**What the 45/45 shows.** The other team's AC-01 to AC-05, REQ-07 and AC-14 behaviour matches the contract as our tests read it. It says nothing about their AC-16 behaviour (persistence, reset, response time), which we haven't run against them.

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
- **Cross-team:** 45/45 of our suite on their system. Tester runs in both directions are still pending.

**Changes from the Phase 2 plan.**
- **Specification source:** the Phase 2 pod contract v1.0, because no instructor OpenAPI file was available (issue #1).
- **Hosting:** Google Cloud Run and Cloud SQL. Note: the course overview slide says "deployed to AWS"; this should be checked with the instructor if it's a hard requirement.
- **Auth-first precedence:** the API key is checked before routing, validation or lookup (issue #4, matching Model 4).
- **AC-16 as scripts, not pytest tests:** a restart has to happen between steps.
- **Course testing interface added**, which wasn't in the Phase 2 pod contract: system `/test/*` endpoints and a deployed tester. The new `test_sessions` table comes in migration 0002.

**Unfinished scope.**
- Phase 4 operations: decisions, corrections, deadline status, filing, timeline. 409 state rules aren't exercised.
- `GET /incidents` isn't in the contract (issue #2).
- Length limits are placeholders (issue #3), so there are no boundary tests.
- Cross-team tester runs haven't happened in either direction, and the destructive `/reset` and AC-16 cross-team runs haven't been done.
- Component coverage in tester reports is null, because the pod spec defines no component list.
- The class registry entry was still marked "TODO: confirm submitted" in Q2.

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
6. Confirm the hosting requirement (AWS vs Google Cloud) and the registry submission.

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
```

## Part 5: Live spot checks (raw HTTP observations)

Captured by Mohit with `curl` while compiling this file, without any API key.

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

## Part 6: Latest CI run (raw log excerpt)

GitHub Actions run 39184911384 on `integration` at `c4b6643`, success, 57 s. Lines are `step | output`, filtered to results. In the JSON, per-operation p50 values are 0.9 ms (health), 2.9 ms (GET incident) and 4.6 ms (POST evidence), with counts 10, 150 and 40.

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

Output of `uv run pytest --collect-only -q` on `integration`. Tests in `tests/acceptance/` other than `test_client_selftest.py` carry the `acceptance` marker (48).

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
  non-root user. 1 vCPU, 512 MiB, min 1 / max 2 instances. One instance is kept
  warm so no request waits for a cold start (REQ-15).
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
  The persistence and performance runs below were against the previous
  deployment, `f2b607c`, which had the same API (the only change since is the
  /docs Authorize button).

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

## Validation against the deployment (2026-10-18)

| Check | Result |
| --- | --- |
| Acceptance suite (`pytest -m acceptance`, AC-01 to AC-05, AC-14) | **48 passed**, 0 failed, 0 skipped |
| Restart persistence (AC-16) | 100/100 incidents intact after restart; 0 after reset |
| Performance (AC-16): 100 incidents loaded, 200 sequential requests from a laptop | **200/200 within 1 s** (needs 95%); p50 48 ms, p95 61 ms, max 76 ms; 0 errors |

One unexplained event: on the first persistence run, one request timed out on
the client side (10 s), so that run was repeated. Cloud Run's request logs for
that period show no request slower than 0.36 s, so the delay was most likely on
the network path between the laptop and Google, not in the service. It did not
recur.

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
  `docs/cross-team-testing.md`). TODO: confirm submitted.
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
(local run: 168 unit/infrastructure tests and 47 acceptance tests passed; against the deployment on 2026-10-18: 48 acceptance tests passed, none skipped). "Yes" means implemented
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
| Data kept across restarts until reset (REQ-15) | **Yes**, deployed | 2026-10-18: 100/100 incidents intact after a Cloud Run restart (new revision), 0 after reset (`scripts/check_persistence.py`) |
| 95% of requests within 1 s at 100 incidents (REQ-15) | **Yes**, deployed | 2026-10-18: 200/200 within 1 s; p50 48 ms, p95 61 ms (`scripts/performance.py`) |
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

### `docs/submission/q4-automated-validation.md`

```markdown
# Q4 Automated validation (draft)

Lead: Mohit. Detailed results: `docs/test-results/`. Requirement mapping: `docs/test-results/traceability.md`.

## What runs, and where

| Layer | Location | Count | Needs |
| --- | --- | --- | --- |
| Unit tests (schemas, routes, repository) | `tests/unit/` | 81 | Nothing |
| Infrastructure tests (auth, errors, logging, database, migrations, course testing interface) | `tests/infrastructure/` | 63 | A disposable PostgreSQL for the database tests (`TEST_DATABASE_URL`) |
| Fixture checks (shared JSON cases follow the contract's field rules) | `tests/fixtures/` | 31 | Nothing |
| Script self-tests | `tests/scripts/` | 7 | Nothing |
| Tester service tests (Srihari) | `tests/tester/` | 25 | Nothing |
| HTTP client self-tests | `tests/acceptance/test_client_selftest.py` | 5 | Nothing |
| **Acceptance suite** (AC-01 to AC-05, AC-14, plus `/health` and `/reset`) | `tests/acceptance/`, marker `acceptance` | 48 | `BASE_URL`, `API_KEY`. Reset tests also need `ALLOW_DESTRUCTIVE_TESTS=1` |
| **AC-16 scripts** (restart persistence, reset, response time) | `scripts/check_persistence.py`, `scripts/performance.py` | — | `BASE_URL`, `API_KEY`. The restart happens between the `create` and `verify` steps |

Our deployed tester (https://incident-tester-356019173418.us-central1.run.app, Srihari) wraps the same suite behind the course testing interface (`POST /test/setup`, `POST /test/run`, `GET /test/report`); see `docs/cross-team-testing.md`. The acceptance suite only talks HTTP to a base URL, so the same tests run against a local app, CI, our deployment, or the other team's deployment. The shared inputs are plain JSON in `tests/fixtures/data/`.

## Continuous integration

`.github/workflows/ci.yml` runs on every push to `main` and `integration`, and on every pull request:

1. Static checks: `ruff check`, `ruff format --check`, `mypy` (strict).
2. The 212 non-acceptance tests, against a disposable PostgreSQL service.
3. Migrates and starts the app inside the job, then runs the 48 acceptance tests against it with a throwaway key.
4. AC-16 smoke test: creates 100 incidents, restarts the app, verifies them, resets, then runs the response-time check.

Latest run on `integration` (`c4b6643`, 2026-10-19 UTC): all green. 212 passed; acceptance 47 passed, 1 skipped (the HTTPS check skips for a local target); 100/100 persisted; 200/200 within 1 s. CI never calls a deployed service.

## Results

| Date | Target | Acceptance | Persistence | Response time |
| --- | --- | --- | --- | --- |
| 2026-10-16 | Local Docker Compose | 47 passed, 1 skipped (HTTPS) | 100/100 after app and full-stack restarts | 200/200 within 1 s, p95 16 ms (loopback) |
| 2026-10-18 | Our deployment (Cloud Run) | **48 passed**, 0 skipped | **100/100** after a revision restart; all removed by reset | **200/200 within 1 s**, p95 61 ms |
| 2026-10-18 | Our deployment (`f551649`), through our deployed tester | **48 pass**; code coverage 135/522 lines; 8/16 ACs exercised | — | — |

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
```

### `docs/submission/q6-cross-team-readiness.md`

```markdown
# Q6 Cross-team readiness

Lead: Mohit. Working checklist and raw results: `docs/test-results/cross-team.md`.

Both teams built from the same specification, the Phase 2 pod contract v1.0. The other team's service publishes its copy at `/openapi.yaml`. It lists the same operations, fields and rules we built from, so neither team has added anything to the shared interface.

## Testing in both directions

| Direction | What happened | Result |
| --- | --- | --- |
| Our tests → their service (https://incident-clock.onrender.com) | 2026-10-18: our acceptance suite, run non-destructively | **45 passed, 0 failed, 3 skipped.** The skips are the `/reset` tests, left out on purpose so we didn't wipe their data. [Details](../test-results/2026-10-18-cross-team-ours-on-theirs.md) |
| Their tests → our service (https://incident-api-356019173418.us-central1.run.app) | Their tester (https://incident-clock-tester.onrender.com) uses the course testing interface. Our system added `/test/setup` and `/test/report` on 2026-10-18 (`f551649`). We gave them our URLs and, privately, a key | **Not run yet.** Waiting for their tester to target us |
| Our tester → our service (check of the interface) | 2026-10-18: our deployed tester (https://incident-tester-356019173418.us-central1.run.app) ran a full session against our system | **48 pass**; code coverage 135/522 lines; 8/16 ACs exercised (`docs/cross-team-testing.md`) |
| Our tester → their service | Needs their key in our Secret Manager and their URL in the tester's approved list | **Not run yet** |

Our suite only checks the outside behaviour of an operation, so the 45 passes are evidence that their AC-01 to AC-05 and AC-14 behaviour matches the contract as we read it. That includes AC-14's HTTPS check. They aren't evidence about AC-16 (persistence, reset, response time), which we haven't run against them.

## Specification ambiguities and their status

| Topic | What the contract says | Our service | Their service | Status |
| --- | --- | --- | --- | --- |
| Course testing interface (`/test/setup`, `/test/report`) | Defined by the course's "Cross-team Testing Interface" spec, not the pod contract | Implemented (Srihari) | Implemented | Both sides have it. Session semantics: one active session; setup resets data; a reused ID is 409. Errors on `/test/*` use `{message, source}` |
| `GET /incidents` (issue #2) | Not defined, though AC-02 and AC-16 refer to listing incidents | Not implemented (405) | Not in their spec | Both left it out, so the services agree. The AC-02 count check and AC-16's "no incidents remain" are checked one ID at a time instead |
| Field length limits (issue #3) | Not specified | Title ≤ 200, description ≤ 5000 (placeholders) | Only "not empty"; maximums left open | **Open.** Longer valid input would be accepted by them and rejected by us with a 400 |
| Unknown extra fields | Not specified | Ignored | Not specified in their spec | Unconfirmed. No failures seen |
| Error code names | Only `{error, message}` is required | `UNAUTHORIZED`, `NOT_FOUND`, `METHOD_NOT_ALLOWED`, `INVALID_<FIELD>` | `UNAUTHORIZED`, `NOT_FOUND` seen; also `INVALID_SESSION_ID` | Our tests check the shape, not the exact code. Unconfirmed whether their tests check exact codes |
| Health body | `{status: string}` | `"OK"` | `"ok"` | Both are valid |
| Reset coordination | `/reset` clears all data | — | — | **Open.** No time window has been agreed for destructive runs in either direction |

## Still open

These are recorded as they stand at submission, not as resolved.

- Their tester's run against our system, and our tester's run against theirs (their key into Secret Manager, their URL into `ALLOWED_TARGETS`).
- Agree length limits and the reset window with the other team, then run our `/reset` tests and AC-16 scripts against them.
- Record their results against our service, including failures and who owns each one, once they can run.
```

### `docs/submission/q7-status-and-limitations.md`

```markdown
# Q7 Status and limitations

Consolidated by Mohit from the Q2–Q6 sections and `docs/test-results/`. Srihari and Astha: please check the lines about your areas.

## Current status (2026-10-18)

- **Delivered:** every Phase 3 operation in the pod contract: `GET /health`, `POST /incidents`, `GET /incidents/{id}`, `POST /incidents/{id}/evidence`, `POST /reset`. They're backed by PostgreSQL, with API-key auth, `{error, message}` errors and 405 for edits and deletes.
- **Deployed:** Google Cloud Run with Cloud SQL, over HTTPS, at https://incident-api-356019173418.us-central1.run.app. The running commit is shown in the `X-App-Commit` header.
- **Validated:**
  - 48/48 acceptance tests passed against the deployment.
  - 100/100 incidents were intact after a restart.
  - 200/200 requests completed within 1 s (p95 61 ms).
  - CI runs static checks, 170 unit/infrastructure tests, the acceptance suite and an AC-16 smoke test on every push.
- **Course testing interface:** our system has `POST /test/setup` and `GET /test/report`, and our tester is deployed at https://incident-tester-356019173418.us-central1.run.app. A full session against our system gave 48 pass, code coverage 135/522 lines, 8/16 ACs (Srihari, `docs/cross-team-testing.md`).
- **Cross-team:** our suite passed 45/45 against the other team's service. Their tester hasn't run against ours yet, and our tester hasn't run against theirs (see Q6).

## Changes from the Phase 2 plan

- **Specification source:** no instructor OpenAPI file was available, so we built from the Phase 2 pod contract v1.0. The other team did the same (`docs/contract-issues.md` #1).
- **Hosting:** Google Cloud Run and Cloud SQL, chosen and run by Srihari (`docs/deployment.md`).
- **Precedence where the contract is silent:** the API key is checked before routing, validation or lookup (`docs/contract-issues.md` #4).
- **AC-16 checks are scripts, not pytest tests:** a service restart happens partway through, so they're `scripts/check_persistence.py` and `scripts/performance.py`.

## Unfinished scope

- **Phase 4 operations:** decisions, corrections, deadline status, filing and timeline. Not implemented, and 409 state rules aren't exercised yet.
- **Tester runs across teams:** neither tester has run against the other team's system yet.
- **Component coverage** is reported as null, because the pod spec defines no component list.
- **`GET /incidents`** isn't in the contract (issue #2). AC-02's count check and AC-16's "no incidents remain" are checked per ID instead.
- **Length limits:** placeholders (title 200, description 5000) until the pod agrees (issue #3), so boundary tests aren't written.
- **Destructive cross-team runs:** our `/reset` tests and AC-16 scripts haven't run against the other team. No reset window has been agreed.

## Known defects and risks

- **Clock-sensitive database test:** `tests/infrastructure/test_feature_database.py` compares a database timestamp with the test machine's clock. It failed once locally because a Docker database clock was a few seconds off. It passes in CI. It needs a small tolerance (Astha).
- **One client-side timeout:** during the first deployed persistence run, one request timed out at 10 s. Cloud Run's logs showed no request slower than 0.36 s, so it was most likely the network path. The run was repeated and passed (Q2).
- **Coverage is per instance and in memory:** the service runs `max-instances 1` so a session's coverage stays on one instance, and a restart clears it (Srihari).
- **`HEAD /health` returns 405.** Only `GET` is in the contract, so this is not a contract defect, but some uptime checkers use `HEAD`.
- **Synthetic data on the other team's service:** our non-destructive run left test incidents in their database.

## Adjustments for Phase 4

1. Run both teams' testers against each other's systems and record the results.
2. Settle issues #2 and #3 with the other team, then add length-boundary tests and, if agreed, a list check.
3. Implement decisions, corrections, deadline status, filing and timeline. Extend the shared fixtures and acceptance suite with the AC criteria for them, including 409 state rules.
4. Agree a reset window and run both teams' destructive tests and AC-16 in both directions.
5. Add a timestamp tolerance to the clock-sensitive database test.
```

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
| 2026-10-18 | Our deployment (`ed5f449` / `f2b607c`) | [48/48 acceptance, 100/100 persisted, 200/200 under 1 s](2026-10-18-deployed.md) |
| 2026-10-18 | Other team's deployment (incident-clock) | [Our suite: 45 passed, 0 failed, 3 skipped (reset, on purpose)](2026-10-18-cross-team-ours-on-theirs.md) |

CI also runs the acceptance suite and an AC-16 smoke test (persistence across an app restart, reset, response time) against an app inside the CI job on every push. Those runs are regression checks, not recorded results.
```

### `docs/test-results/traceability.md`

```markdown
# Requirement / test traceability

Owner: Mohit. Feeds submission Q4. Status covers local, CI and deployed runs. Each run is recorded in this folder.

| Criterion | Planned coverage (README §5) | Tests | Status |
| --- | --- | --- | --- |
| AC-01 – AC-04 | Incident create/retrieve workflow, including success, failure, and boundary cases | Fixtures: `tests/fixtures/data/incidents_*.json`, `evidence_valid.json` and `test_ac01_05_incidents_evidence.py` | Written. All pass locally and against the deployment. Length boundaries wait on issue #3. AC-02's count check waits on issue #2 |
| AC-02 | Includes listing incidents | — | Blocked: `GET /incidents` existence (issue #2) |
| AC-03 (GET half) | Unknown incident ID returns 404 with error code and message | `test_system_endpoints.py::test_unknown_incident_get_is_404_with_error_format` | GET half passes against the app run locally and in CI. POST half is in `test_ac01_05_incidents_evidence.py` |
| AC-05 | Evidence attachment, where the increment supports it | Fixtures: `tests/fixtures/data/evidence_*.json` and `test_ac01_05_incidents_evidence.py` | Written. All pass locally and against the deployment |
| AC-14 | Public health endpoint | `test_ac14_security.py::test_health_is_public` | Passes locally, in CI and against the deployment ([2026-10-18](2026-10-18-deployed.md)) |
| AC-14 | Missing / wrong / valid API key | `test_ac14_security.py::test_authenticated_route_*` | Passes against the app run locally and in CI; assumes auth before 404 (issue #4) |
| AC-14 | HTTPS deployment | `test_ac14_security.py::test_deployment_uses_https` | Passes against the deployment ([2026-10-18](2026-10-18-deployed.md)); skips for local targets |
| AC-16 | Reset | `test_system_endpoints.py::test_reset_*` (destructive, opt-in); `scripts.check_persistence reset` (each created ID returns 404 afterwards); Srihari's `tests/infrastructure/test_database.py` | Passes locally ([2026-10-16 run](2026-10-16-local-ac16.md)) and in CI. "No incidents remain" is checked per ID until issue #2 is settled |
| AC-14 | Errors use `{error, message}` | `test_system_endpoints.py::test_401_uses_error_format` | Passes against the app run locally and in CI |
| AC-16 | Restart persistence | `scripts.check_persistence create` / restart / `verify` | 100/100 intact after an app restart and after a full stack restart, run locally ([2026-10-16](2026-10-16-local-ac16.md)). In CI after an app restart. Deployed: 100/100 after a Cloud Run revision restart ([2026-10-18](2026-10-18-deployed.md)) |
| AC-16 | Response time (100 incidents, 200 requests) | `scripts.performance` | 100% within 1 s, run locally ([2026-10-16](2026-10-16-local-ac16.md)). Smoke run in CI. Deployed: 200/200 within 1 s, p95 61 ms ([2026-10-18](2026-10-18-deployed.md)) |

Before any service existed, the AC-14 tests were checked two ways. Against a throwaway local stub with `/health` and key checking, they passed (HTTPS check skipped). Against the current scaffold, which has no routes, they failed as expected. Neither run is a result for the real service.
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
# 2026-10-18: acceptance and AC-16 runs against our deployment

Owner: Mohit. **Target: our deployed service**, https://incident-api-356019173418.us-central1.run.app (Google Cloud Run + Cloud SQL, see `docs/deployment.md`).

The suite and scripts are Mohit's (`tests/acceptance/`, `scripts/`). Srihari ran them against the deployment, because the shared test key lives in Secret Manager and he has `gcloud` set up. His numbers are copied from `docs/submission/q2-deployment.md`. Mohit's own checks below need no key.

## Conditions

| | |
| --- | --- |
| Date | 2026-10-18 |
| Server code | Acceptance suite: `ed5f449` (`integration`). Persistence and performance: `f2b607c`, which has the same API. The only change between them is the `/docs` Authorize button |
| How the commit was checked | `X-App-Commit` response header |
| Client | A laptop over the public internet, so network latency is included |

## Results (run by Srihari)

| Check | How | Result |
| --- | --- | --- |
| Acceptance suite | `pytest -m acceptance` with `ALLOW_DESTRUCTIVE_TESTS=1` | **48 passed**, 0 failed, 0 skipped. The HTTPS check ran and passed |
| Restart persistence | `check_persistence create` (100 incidents), new Cloud Run revision (`incident-api-00002-msv` → `incident-api-00003-ggj`), then `verify` | **100/100 intact** |
| Reset | `check_persistence reset` | All 100 removed |
| Response time | `scripts.performance`: 100 incidents, 200 sequential requests | **200/200 within 1 s** (target 95%), 0 errors. p50 48 ms, p95 61 ms, max 76 ms |

On the first persistence run, one request hit the client's 10 s timeout, so the run was repeated. Cloud Run's logs for that period show no request slower than 0.36 s, which points to the network path rather than the service. It didn't happen again.

## Spot checks without the key (run by Mohit, 2026-10-18)

| Request | Expected | Observed |
| --- | --- | --- |
| `GET /health` | 200 `{"status": ...}`, no key needed | 200 `{"status":"OK"}` |
| `GET http://…/health` | Redirect to HTTPS | 302 to `https://…/health` |
| `GET /incidents/INC-001` with no key | 401 `{error, message}` | 401 `{"error":"UNAUTHORIZED","message":"missing or invalid API key"}` |
| `GET /incidents/INC-001` with a wrong key | 401 `{error, message}` | 401, same body |
| `X-App-Commit` header | The deployed commit | `ed5f449` |

## Caveats

- "No incidents remain after reset" is still checked per ID, because there's no list route (`docs/contract-issues.md` #2).
- Response times come from one laptop at one time of day. They show the target is met with plenty of margin, not what every client will see.
- Mohit hasn't run the keyed suite himself yet. That needs the key from Srihari over a private channel.
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
- [ ] An agreed time window for runs that call `POST /reset`, so neither team wipes the other mid-run.
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
| Their tests → our service | Our system now has `/test/setup` and `/test/report` (Srihari, `f551649`). Waiting for their tester to run against us |
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
- Running again: `409`. The stored report matches the run response.
- Non-approved target: `400`.
- Our system's `/test/setup` without a key: `401` with `source: system`.
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

The HTTP client (`tests/acceptance/client.py`) and fixtures (`conftest.py`) are in the repo. These are the files that make the assertions.

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

Fetched by Mohit on 2026-10-18 from `https://incident-clock.onrender.com/openapi.yaml` (433 lines; it needs their key, which isn't reproduced here). Below: the header verbatim, every operation and summary, and the schemas relevant to Q6. Note that there is no `GET /incidents`, no `/test/*`, and title/description have `minLength: 1` with the max left open.

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


paths:  # operations only (full file has responses for each)
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
