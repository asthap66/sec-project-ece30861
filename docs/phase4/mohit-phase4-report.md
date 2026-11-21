# Mohit Phase 4 handoff — 2026-11-01

**Updated after source PDFs were supplied:** see [contract review](contract-review.md)
and the final verification addendum below. They supersede historical missing-artifact,
provisional-schema and unresolved-state/boundary statements in the initial report.

## Branch and source inventory

Branch: `mohit-phase4`. Base: fetched `origin/integration`,
`e9dd257d6840f41369d6be700dc5d28ec226db42`. Working tree was clean on arrival
on main. Integration contains the current persistent Phase 3 implementation,
confirmed by history, migrations, tester and submission documents. No shared
branch was modified. The Phase 4 plan was copied unchanged from main except
for code-block spacing required by Ruff and a Mohit-only handoff note.
No applicable AGENTS.md was found in the repository or ancestor directories.

Read README, setup, intra-pod specification, contract issues, feature/model,
submission/testing/cross-team documentation, test helpers and fixtures, workflows,
lock configuration, migrations, application routes/services, and tester
setup/run/report and Docker packaging. No original Phase 2 PDF/DOCX, Phase 4
course milestone artifact, or instructor OpenAPI file exists in this checkout.
The rubric Google Docs URL in the plan was inaccessible when fetched. Generated
OpenAPI represents implementation, not approval of future behavior. Existing
contract issue 1 records the team's Phase 2 v1.0 fallback. Phase 4 assertions
use the explicitly quoted domain rules in plan section 5 and the user's
reference cases; they require comparison with the original sources before
cross-team conformance claims. This is a material evidence limitation.

## Implemented work

- `tests/acceptance/test_phase4_decisions.py`: 37 HTTP cases selected by
  `phase4`, using the existing client, public setup, returned IDs and assertions.
  Material success/current decision, seven manual calendar inputs, 18 negative
  requests, repeat-decision conflict, evidence-only workflow, pending/overdue,
  authentication/resource failures, NOT_MATERIAL partial checks and reset.
- Negative requests re-read the complete incident before/after rejection;
  conflict checks preserve the original decision. Observable equality does not
  prove absence of orphan rows; Srihari must verify transactional persistence.
- `tests/fixtures/data/phase4_deadlines.json`: independently enumerated fourth
  business days, provenance, UTC/Eastern midnight and equivalent-offset inputs.
  No production calendar imports. Fixture test validates chronology, offsets,
  uniqueness, count, weekdays and deadline consistency. October 13, November 27
  and January 1 exclusions reproduce the supplied examples; holiday-list
  approval remains pending, especially the documented 2025 versus 2026–27 gap.
- Marker registered without new dependencies or lockfile changes.
- Existing tester recursively discovers the file and Docker already packages
  its fixtures: no runner or deployment changes needed. Small shared changes
  to review with Srihari: result duration, JSONL start/end metadata (UTC time,
  real elapsed time, configured target and tester SHA), report outcome counts,
  and wording that criterion exercise is partial, not full verification.
  The course report response contract and setup/run interfaces stay compatible.
  Metadata is retained in the JSONL sidecar; it is not added to the public
  report. Target version is unavailable there; save X-App-Commit separately.
- CI preserves Phase 3 blocking steps and adds an explicit informational
  Phase 4 selection plus JUnit/JSONL artifact. The existing disposable DB is
  used sequentially; separate workflow runs have separate service containers.
  No xfail or missing-route skip. Phase 4 failures deliberately do not fail
  the checks job yet. Make this step required by removing continue-on-error
  after integration. Shared deployed sessions still require a reset window.

## Requirement and acceptance mapping

| Test function suffix / group | Requirement | Criterion and limit |
| --- | --- | --- |
| material_decision_calendar | REQ-04/09 | AC-06 retrieval; AC-09 standard; AC-10 holiday/weekend cases (not fully source-confirmed) |
| invalid_decision_no_observable_write; invalid_references_and_future | REQ-05 | AC-06 invalid fields, timestamps and evidence |
| not_material_has_no_applicable_deadline | REQ-04/10 | AC-06 partial: state enum and full schema unresolved |
| evidence_does_not_decide | REQ-04 | AC-07 HTTP observation plus source inspection required |
| second_ordinary_decision_preserves_original | REQ-08 | AC-15 partial: no filing-dependent transitions |
| deadline_status_without_filing | REQ-10 | AC-11 overdue-only; pending also exercised |
| phase4_authentication; phase4_unknown_incident | REQ-13/14 | AC-14/AC-03, not proof routes exist |
| reset_removes_decided_incident | REQ-14/15 | AC-16 reset portion only |
| existing Phase 3 suite/scripts | REQ-01/02/03/07/13/14/15 | Existing regression retained; AC-08 remains partial without corrections |

Existing report's 16-criterion denominator is a count of partially exercised
criteria only; failures can count as exercise. It is never a conformance rate.
Component and unavailable code coverage remain null with explanations.

## Verification evidence

Disposable database: `POSTGRES_PORT=55434 docker compose -p mohit-phase4 up -d db`.
No shared or deployed service was contacted for writes. Local server on port
8044 used that container and a throwaway key. Commands from documented uv,
Compose, Alembic and script interfaces:

| Command | Actual result |
| --- | --- |
| `uv sync --locked` | Passed, no lock change |
| `uv run pytest --collect-only -q` | 300 tests collected (37 Phase 4) |
| `TEST_DATABASE_URL=<disposable URL> uv run pytest -m 'not acceptance'` | 215 passed, 85 deselected after final additions |
| `BASE_URL=http://127.0.0.1:8044 API_KEY=<local key> ALLOW_DESTRUCTIVE_TESTS=1 uv run pytest -m 'acceptance and not phase4'` | 47 passed, 1 local HTTPS skip, 252 deselected |
| Same environment, `uv run pytest -m phase4 --junitxml=/tmp/mohit-phase4.xml` | 31 failed, 6 passed, 263 deselected; no blanket skips |
| `API_KEY=<local key> DATABASE_URL=<disposable URL> uv run alembic upgrade head` | Passed; head 0002 |
| `uv run ruff check .` | Passed after changes |
| `uv run ruff format --check .` | Passed after changes |
| `uv run mypy` | Passed, 63 source files |

One existing Starlette/httpx deprecation warning occurs. An initial standalone
migration command omitted API_KEY and failed settings validation; rerun with
the documented required settings passed. Raw run files are under `/tmp/mohit-*`,
not tracked. Collection success is not execution success.

All 31 Phase 4 failures encounter absent routes: expected 201/400/200 receives
404. Six passes are four auth checks and two unknown-ID checks. They can pass
through generic middleware/router behavior and are not feature completion.
No production decision service, calendar or migration was implemented here.
Phase 3 source inspection finds currentDecision fixed to null and no automatic
materiality engine; repeat this review after features merge for AC-07.

## Blockers and integration actions

| ID / affected package | Missing behavior / owner | Work completed now | Unblock and verification |
| --- | --- | --- | --- |
| F1 decision success/negative/conflict cases | Decision validation, endpoint and currentDecision: Astha; rows/transactions: Srihari | Tests implemented and executed with missing-route failures | Implement owned production features; rerun phase4; inspect rejected writes transactionally |
| F2 calendar/status cases | Calculator, holidays: Srihari; endpoint: Astha | Manual oracle and status tests implemented | Compare original holiday artifact, implement calculator/wiring, rerun fixed-date cases |
| F3 reset/persistence | Decision migration/reset: Srihari | HTTP reset test implemented | Apply migration; reset decided incidents; verify DB has no dependent rows; restart with same IDs before reset |
| C1 NOT_MATERIAL/state schemas | Original Phase 2 state model/success and detail schemas: both teams, Astha coordinates | Partial success/current decision and NOT_APPLICABLE checks | Obtain source, assert exact state and nullable deadline fields; define repeat ordinary decision after NOT_MATERIAL |
| C2 date boundaries | Due-date instant, businessDays, future as_of, full NOT_APPLICABLE shape: both teams | Explicit historical before/after status tests | Agree/source exact rules then add precise boundaries/counts; no invented values |
| C3 validation edges | Duplicate evidence IDs, undefined text maxima and error vocabulary: both teams | Required fields/types/time/reference rejection tests; shared nonempty error envelope | Retrieve approved contract; add exact rules if specified; do not enshrine implementation-specific codes |
| C4 source artifacts | Original Phase 2/milestone/OpenAPI: Mohit requests from team/course | Inventory and provenance recorded | Compare every field/status with source; update tests only with agreed evidence |
| R1 filing/corrections | Later milestone unless course scope changed: feature owners | Phase 3 no-edit/delete regression preserved | Do not claim all AC-08/11/15; add filing/correction-history scenarios when delivered |
| D1 release/cross-team | Deployment/tester packaging: Srihari; windows/results: Mohit and other team | Local preparation and instructions complete | Deploy reviewed SHAs outside this task; agree window; execute both directions and attach actual evidence |

After feature integration Mohit must run all local tests with disposable DB,
all HTTP tests, source review for AC-07, migration/reset/restart/performance
checks, and resolve schema/calendar blockers before declaring completion.
Review shared tester edits with Srihari. Promote CI enforcement only after
31 missing-feature failures are addressed. No base merge, push or deployment
was performed. Branch-protection API for integration returned HTTP 404; this
cannot distinguish missing protection from unavailable permissions. Required
checks/merge blocking are therefore unverified; administrator should confirm
checks are required. No repository settings changed.

## Repeat-run limitation and additional observations

The first DB regression run passed 215 tests. The final repeat after helper
changes ran 300-test discovery with 85 deselected: **214 passed, 1 failed**.
The existing test
`tests/infrastructure/test_feature_database.py::test_postgres_create_retrieve_evidence_restart_reset`
asserts host `before <= recordedAt <= host now`; it observed host before
`2026-11-01T20:54:27.034674Z` versus database recording time
`2026-11-01T20:54:23.054089Z`. This is a local Docker/PostgreSQL versus host
clock discrepancy, not a missing Phase 4 route. Srihari owns clock diagnosis;
Mohit can rerun after synchronization. No tolerance was added to conceal it.
The verification table's 215-pass entry describes the initial run, not the
final repeat. CI behavior must be observed on CI before claiming success.

Rulesets API returned an empty list; integration branch-protection API returned
404. No enforceable merge protection was established by this inspection.
The currentDecision field assertions are provisional transcriptions of the
planned decision data, pending C1 comparison against the original detail schema.

Additional executed checks:

- `uv run pytest tests/tester tests/fixtures -q`: 59 passed.
- With the documented local BASE_URL/API_KEY, `uv run python -m
  scripts.check_persistence create --state /tmp/mohit-persistence.json`, stop
  and restart the same server without reset, then `verify` with the same
  state path: 100/100 intact. With ALLOW_DESTRUCTIVE_TESTS=1, `reset`:
  100/100 gone. This exercises Phase 3 data only; decisions remain blocked.
- `uv run python -m scripts.performance`: 100 incidents loaded, 200 sequential
  requests, zero errors, 200/200 under 1 second; p50 17.2 ms, p95 40.6 ms,
  max 59.1 ms. Local Darwin arm64/Python 3.12.1, not deployed performance.
- Final plugin-enabled run: `uv run python -m pytest -m phase4 -p
  tester.pytest_plugin --junitxml=/tmp/mohit-phase4.xml`: 31 failed, 6 passed;
  JSONL recorded real duration 2.217 seconds and exit status 1. Initial use of
  the standalone pytest entrypoint could not import the plugin; CI and runbook
  now use the same `python -m pytest` invocation as the existing tester runner.
- Workflow reviewed against existing lock/install/migration/start sequence;
  GitHub Actions itself was not run. Lint, format, type and diff whitespace
  checks passed. No secrets, generated reports, production changes or dependency
  changes are included. Local Docker resources were stopped after verification.

Commits: the plan carry-forward and the focused tests/CI/report implementation
are committed on mohit-phase4; use `git log origin/integration..mohit-phase4`
for exact identifiers (the report does not embed its own commit hash).

## Final source-backed verification addendum

After Mohit supplied all three source PDFs, the suite was aligned with Q3.2,
Q4, Q5.2 and Q6.2. See [contract-review.md](contract-review.md) for the source
comparison and unresolved questions. The full state/schema/date-boundary
blockers in C1/C2/C4 above are historical: NOT_MATERIAL, subsequent MATERIAL,
currentDecision fields, null deadline and the Eastern date boundary are now
resolved. Remaining ambiguity is narrower and listed in the contract review.
The course tester OpenAPI starter is available in the supplied course PDF;
no independent domain OpenAPI file was supplied.

Final executions on the same isolated Compose database and port-8044 server:

| Command | Result after source alignment |
| --- | --- |
| `uv run pytest --collect-only -q` | 308 tests, including 45 Phase 4 |
| `TEST_DATABASE_URL=<disposable URL> uv run pytest -m 'not acceptance'` | 214 passed, 1 failed, 93 deselected; same existing host/database timestamp assertion |
| `BASE_URL=<local URL> API_KEY=<local key> ALLOW_DESTRUCTIVE_TESTS=1 TESTER_RESULTS_FILE=/tmp/mohit-contract-phase4.jsonl uv run python -m pytest -m phase4 -p tester.pytest_plugin --junitxml=/tmp/mohit-contract-phase4.xml` | 39 failed, 6 passed, 263 deselected; elapsed 2.442 seconds; all failures encounter missing feature routes |
| Same local URL/key and destructive opt-in, `uv run pytest -m 'acceptance and not phase4'` | 47 passed, 1 local HTTPS skip, 260 deselected |
| `uv run ruff check .` | Passed |
| `uv run ruff format --check .` | Passed, 99 files |
| `uv run mypy` | Passed, 63 source files |
| `git diff --check` | Passed |

Eight added cases cover empty required text, NOT_MATERIAL-to-MATERIAL,
three Model 3 business-day examples and both sides of Eastern midnight.
Existing tests now assert the source-defined NOT_MATERIAL enum, nullable
applicable deadlines, full decision fields, invalid-enum error example and
field-naming errors. All 45 cases are implemented and executed; only the six
auth/resource checks pass on the current baseline. These do not prove routes
exist. No filing-dependent or correction-history completion is claimed.

Mohit authorized pushing the branch and opening a **draft** PR targeting
integration. The PR explicitly retains the missing-feature failures, repeated
timestamp failure and informational Phase 4 CI status. No merge or deployment
is authorized by that action. Follow-up source files remain private local inputs;
repository documentation records their relevant sections without copying PDFs.

## Calendar setup correction for PR #13

Teammates identified a test bug in `setup_decision()`: it used the default
`VALID_INCIDENTS[0]`, whose discovery is September 21, 2026, with a default
September 29, 2025 determination and seven 2025 calendar cases. A conforming
decision endpoint would reject those supposed successes with 400. The earlier
404 missing-route runs stopped before decision validation and **did not establish
that all fixtures or success requests were valid**. The earlier fixture test
checked manual dates against a separate historical constant, not the discovery
actually sent by `setup_decision()`. That gap is corrected here.

`create_phase4_incident()` now copies the source Case and both its body/expected
dictionaries before overriding discovery with `2020-01-01T00:00:00Z`.
`setup_decision()` uses that copy for all its callers. The evidence-only AC-07
case also uses it, so its historical as_of is after discovery. The post-reset
fresh-incident assertion has no determination/as_of and retains the Phase 3
fixture. No shared fixture, reference determination or expected deadline changed.
The explicit 1900 before-discovery rejection remains before discovery; the
future-decision rejection still generates now plus 365 days.

Contract check: REQ-02/Q5.2 require timezone-aware nonfuture discovery;
REQ-05 requires determination not before discovery or in the future. The
strictly earlier historical discovery avoids the unresolved equality case.
The existing evidence contract imposes no collectedAt-versus-determination
ordering requirement (`docs/intra-pod-spec.md` and `docs/incident-evidence.md`);
no extra timestamp restriction was invented. All shared setup callers,
including NOT_MATERIAL, repeated decisions, pending/overdue, Model 3 and Eastern
boundary success cases, were inspected for chronology.

Added `test_phase4_setup_chronology_and_shared_fixture_isolation` exercises
the actual setup helper using the existing MockTransport client pattern. It
captures discovery sent on two calls, confirms shared cases stay unchanged,
checks all calendar/default/Model 3 valid determinations are later and historical,
and checks the before-discovery input still predates discovery. This is a
regression check for test setup only, not evidence that feature routes work.

Actual verification on the unchanged production baseline, disposable Compose
project `mohit-phase4`/PostgreSQL port 55434, local API port 8044:

| Command | Result |
| --- | --- |
| `uv run pytest tests/fixtures tests/tester -q` | 60 passed |
| `uv run pytest --collect-only -q` | 309 collected; 45 Phase 4 unchanged |
| Local BASE_URL/API_KEY and ALLOW_DESTRUCTIVE_TESTS=1, `uv run pytest -m 'acceptance and not phase4'` | 47 passed, 1 local HTTPS skip, 261 deselected |
| Same local settings, `uv run python -m pytest -m phase4 --junitxml=/tmp/mohit-chronology-phase4.xml` | 39 failed, 6 passed, 264 deselected; all failures still encounter absent decision/deadline routes |
| Local DATABASE_URL/API_KEY, `uv run alembic upgrade head` | Passed |
| `uv run ruff check .` | Passed |
| `uv run ruff format --check .` | Passed, 99 files |
| `uv run mypy` | Passed, 63 source files |
| `git diff --check` | Passed |

The existing Starlette/httpx deprecation warning remains. The historical DB
clock/timestamp regression failure is not resolved or rerun by this focused
fix. No production feature, CI behavior, migration, reference calendar data,
merge or deployment change is included. Local server/container were stopped
after verification. The fix is committed and pushed to the existing PR #13.
