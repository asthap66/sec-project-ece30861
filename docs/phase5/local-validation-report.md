# Mohit Phase 5 local validation — 2026-11-21

Branch: `mohit-phase5-work`. Fetched `origin`; merged `origin/integration`
(`2825e67`) into the Phase 5 branch because `origin/main` held the new work
plan but the working Phase 3/4 implementation was on integration. The branch
has not been pushed, merged upstream or deployed.

## Completed independent work

- Reviewed the Phase 5 plan, Phase 4 reports/models, current production code,
  generated OpenAPI and tester/test/CI structure. The generated OpenAPI has no
  correction, filing or timeline operation. No final Phase 5 domain OpenAPI or
  teammate schema handoff is checked in.
- Added a fixed synthetic scenario fixture for original/corrected decisions,
  four filing date positions, invalid/duplicate scenarios, timeline ordering,
  and restart/reset expectations. Six fixture tests validate independent data
  without importing the production calendar or route code.
- Registered the `phase5` marker and added an enforcing CI fixture selection
  with JUnit and JSONL artifacts. The existing Phase 3/4 test selections and
  tester interface remain intact.
- Recorded the requirement/test matrix, contract/model questions and a
  cross-team runbook. No API, migration, deployment setting or production
  behavior was changed.

## Executed verification

All commands were run from the repository root on local Python 3.12.1. The
database was a new disposable PostgreSQL 16 container in Colima profile
`mohit-phase5`, Compose project `mohit-phase5-local`, host port 55439. `API_KEY`
was a throwaway local value. Actual local URL: `http://127.0.0.1:8049`.

| Command | Result |
| --- | --- |
| `uv run pytest --collect-only -q` | 423 collected |
| `DATABASE_URL=<disposable URL> API_KEY=<local key> uv run alembic upgrade head` | Pass; fresh database upgraded through 0001, 0002, 0003 |
| Same environment, `uv run alembic current` | `0003 (head)` |
| `TEST_DATABASE_URL=<disposable URL> uv run pytest -m 'not acceptance' -q` | 330 passed, 93 deselected |
| `BASE_URL=<local URL> API_KEY=<local key> ALLOW_DESTRUCTIVE_TESTS=1 uv run pytest -m 'acceptance and not phase4' -q` | 47 passed, 1 skipped (HTTPS deployment check on loopback), 375 deselected |
| Same local service settings, `TESTER_RESULTS_FILE=/tmp/mohit-phase5-phase4.jsonl uv run python -m pytest -m phase4 -p tester.pytest_plugin --junitxml=/tmp/mohit-phase5-phase4.xml -q` | 45 passed, 378 deselected |
| All local service/database settings, `uv run pytest -q` | 422 passed, 1 local HTTPS skip |
| `TESTER_RESULTS_FILE=/tmp/mohit-phase5-fixtures.jsonl uv run python -m pytest -m 'phase5 and not acceptance' -p tester.pytest_plugin --junitxml=/tmp/mohit-phase5-fixtures.xml -q` | 6 passed, 417 deselected; [JUnit](../test-results/2026-11-21-phase5-fixtures.xml) and [JSONL](../test-results/2026-11-21-phase5-fixtures.jsonl) copies saved |
| `uv run ruff check .`; `uv run ruff format --check .`; `uv run mypy`; `git diff --check` | All passed; format checked 122 files, mypy checked 75 source files |

The existing `scripts.check_persistence` was also run with `--count 3`: create
returned 3 IDs; the local API process was stopped and restarted without a
database reset; verify reported **3/3 intact**; reset reported **3/3 gone**.
This checks the existing incident flow, not Phase 5 records. The first attempt
to initialize PostgreSQL in the default Colima profile failed because that
profile's Docker disk was full. A new isolated profile allowed all checks
above to run. The prior profile and its data were not pruned.

## Pending and limitations

No Phase 5 route acceptance has been executed or claimed. Astha's correction,
filing and timeline handlers and final schemas, and Srihari's records,
migration/calendar/reset integration are missing from the checked-in base.
Therefore Phase 5 restart, reset isolation, deployed tests, and reciprocal
cross-team tests cannot be verified. The current reset endpoint clears all
records, so the Phase 5 plan's “only synthetic data” isolation requirement
needs a design decision before an assertion can be fixed. No final deployed
revision, tester revision, URLs, credentials or exclusive reset window were
provided. See [matrix](requirement-test-matrix.md) and
[contract review](contract-and-model-review.md) for exact follow-up assertions.

The only pytest skip in the full run is the pre-existing deployment HTTPS
check for a loopback HTTP target. The Starlette/httpx deprecation warning is
pre-existing. The passing Phase 5 fixture selection proves scenario-data
integrity only; it does not prove any Phase 5 API behavior.
