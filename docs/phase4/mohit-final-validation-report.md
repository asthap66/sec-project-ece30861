# Mohit final Phase 4 validation — November 2, 2026 UTC

## Verified source and scope

Clean starting worktree; no repository/ancestor AGENTS instructions were found
in the prior inspection. Fetched origin. PR #14 merged as 1eae0cd, #15 as
89c6a17, and #13 as 50f1c53. Current verified integration/source base is
`50f1c53dd37cd9d96261d677d8d21b1b4633584c`. It contains chronology commit
`47547021093d75b007277ff6d9122126c0c0f4a8`, API implementation, repository/calendar
wiring, migration 0003 and database-clock correction. New branch:
`mohit-phase4-final-validation`. Historical reports are preserved; their
missing-route and clock failures describe earlier code.

Read plan, Mohit report/review/runbook, both teammate handoffs, models,
calendar/service/store, migration, tester packaging, CI and setup/deployment
instructions. Original Downloads PDFs are no longer present; the source review
from the earlier supplied PDF inspection remains available. Exact current
Phase 4 Gradescope prompts are not in the checkout; draft follows user-assigned
labels and historical question headings. No teammate personal GenAI account
was authored.

## Changes

Removed continue-on-error from the now-passing Phase 4 CI selection. The shell
pytest command is not piped or masked, so a failure fails the checks job.
Existing Phase 3 checks and JUnit/JSONL uploads remain. Corrected tester mapping:
four holiday/weekend parameters of test_ac09_material_decision_calendar now map
to AC-10; other parameters map to AC-09. Added a focused mapping test. Counts
remain criterion exercise, not conformance. Prepared Gradescope draft and
sanitized local evidence. No production features changed.

## Executed verification

Local only: Compose project `mohit-phase4-final`, PostgreSQL 16, host port 55435;
API on port 8045, throwaway key. No shared-service setup/reset/writes. Python
3.12.1 on Darwin arm64. Locked install via `uv sync --locked` exited 0. Database
migrations via `API_KEY=<local> DATABASE_URL=<disposable> uv run alembic upgrade
head` exited 0, revision 0003. No dependencies/lockfile changed.

- 2026-11-02 01:50:56 UTC start: `TEST_DATABASE_URL=<disposable> uv run pytest
  -m 'not acceptance'`: exit 0, **323 passed**, 93 deselected, 12.55 seconds.
- 01:51:25–01:51:33 UTC: local BASE_URL/API_KEY/ALLOW_DESTRUCTIVE_TESTS=1,
  `uv run python -m pytest -m acceptance --junitxml=/tmp/mohit-final-http.xml`:
  exit 0, **92 passed, 1 skipped**, 323 deselected. Skip: deployment HTTPS
  test because target is loopback HTTP. Pytest duration 7.37 seconds.
- 01:51:33–01:51:40 UTC: same settings, `uv run python -m pytest -m phase4
  -p tester.pytest_plugin --junitxml=/tmp/mohit-final-phase4.xml`: exit 0,
  **45 passed**, 371 deselected, 6.59 seconds.
- 01:51:40–01:51:46 UTC: `uv run python -m scripts.performance`: exit 0;
  100 incidents loaded, 200 sequential requests, zero errors, 200/200 under
  one second; p50 17.9 ms, p95 49.3 ms, max 84.6 ms. Local, not deployed.
- Ruff lint, format, mypy and whitespace checks exit 0. Initial format check:
  115 files; strict mypy: 74 source files. Starlette/httpx deprecation warning
  remains, no validation failure.

Exact timed commands and exit codes: [manifest](evidence/local-command-manifest.json).
[Performance evidence](evidence/local-performance.json). Logs/JUnit/JSONL remain
under `/tmp/mohit-final-*`; secrets are not stored in tracked evidence.

## Persistence, reset, source review and contract probes

A local-only HTTP probe created two 2020-discovered incidents and evidence,
then an explicit MATERIAL decision with duplicate evidence references. Saved
the complete incident response. Stopped and restarted the uvicorn process
without reset. Retrieved response matched every saved field, UTC determination,
evidence, decisionId, MATERIAL_PENDING_FILING and 2025-10-03 deadline exactly.
Public reset returned 200 and both known IDs then returned 404. SQL inspection
before reset: incidents=2, evidence=2, decisions=1, links=2. After: all four
counts zero. Known-ID HTTP evidence is distinct from DB-wide evidence; IDs
were obtained from setup responses. [Sanitized evidence](evidence/decision-restart-reset.json).
Probe commands: `uv run python /tmp/mohit-final-persistence.py create`, restart
local server with same disposable DATABASE_URL, then the script's `verify`
mode; both exited 0. The script is temporary; requests are described above
and saved snapshot documents expected results.

Chronology fix is present; fixture isolation self-test passes. Clock correction
uses PostgreSQL clock_timestamp before/after and retains the ordered bound
assertion for DB-generated recordedAt, without artificial tolerance. Integrated
DB tests pass. AC-07 source review: evidence paths store evidence only;
DecisionService.record_decision accepts a supplied human decision; decision_status
maps current human decision to state and has no inference/recommendation path.
The severe-evidence HTTP test also passes. This inspection covers current source,
not a proof about future versions.

Calendar version `us-federal-2025-2027.v1`: source has 34 observed federal
holiday dates and states OPM/5 U.S.C. 6103 provenance; excludes one-off closures.
2025 addition satisfies explicit AC dates but is not recorded larger-pod approval.
Range check restricts MATERIAL determination Eastern dates, calculated/traversed
business days (including deadlines crossing out of range), and as_of Eastern
dates for applicable deadlines. It does not restrict incident discovery,
evidence timestamps or NOT_MATERIAL determination through the calculator;
NOT_APPLICABLE returns before checking as_of range. Probe: 2020 discovery
accepted; 2024 MATERIAL determination -> 400 DATE_OUT_OF_RANGE with no decision;
2028 as_of on material incident -> same error; 2020 as_of with no decision ->
NOT_APPLICABLE/null/0. This is a source-confirmed implementation limit, not
an explicitly authorized v1.0 constraint. Srihari/pod must resolve it.

Duplicate IDs are preserved in submitted order; no-decision businessDays=0
observed. General businessDays intervals, zero at due date/weekend overdue,
future as_of within supported years and equality of determination/discovery
are implementation policies where the contract is incomplete. Do not promote
these to shared requirements without agreement. AC-08 correction history and
filing-dependent AC-11/15 remain deferred to Phase 5.

## CI and merge enforcement

Integration baseline CI succeeded:
https://github.com/asthap66/sec-project-ece30861/actions/runs/41371187736
This predates removal of informational Phase 4 handling; it is not evidence
that Phase 4 failures were required. New PR run recorded below after publication.
Integration protection API returned 404; rulesets returned []. No enforceable
merge block established. No repository settings changed.

## Deployment and reciprocal testing

Read-only health/OpenAPI probes on November 2 UTC:
API https://incident-api-356019173418.us-central1.run.app returned health 200,
status OK, X-App-Commit e9dd257; OpenAPI omitted decisions/deadline-status.
Tester https://incident-tester-356019173418.us-central1.run.app returned health
200 and setup/run/report paths in OpenAPI, but no version header. Cloud Run
metadata describe failed: no active gcloud account. API/tester revisions,
current tester SHA and latest packaged test version are not independently
confirmed. Source Dockerfile.tester includes acceptance and fixture directories;
that does not prove deployed image contents. No deployed holiday version claim.

No current exclusive synthetic/reset window found. No shared credentials were
printed, no setup/run calls or writes made. Srihari must provide both deployed
SHAs/revisions, migration/version evidence, tester contents and private access;
Mohit/both teams must agree an exclusive window before full validation. No
Phase 4 reciprocal reports found in repository or reviewed PR comments; older
October records remain Phase 3 evidence only.

For each direction retain target/team, app and tester SHAs, UTC time/session ID,
executed/pass/fail/error/skip with reasons, measured code counts/basis or null,
component counts only with agreed definitions, system criteria exercised versus
fully verified, classified failures/owner and rerun evidence. Runbook already
contains templates. No coverage denominators invented.

Unsent request: “Please provide the Phase 4 API/tester source SHAs and deployment
revisions (including corrected tests and holiday version), privately confirm
target access, and propose an exclusive synthetic-data/reset window for both
reciprocal runs. Please return each session report with versions, UTC time,
counts, coverage basis and failure/rerun details. Please also confirm whether
the pod has decided the list/count issue proposed for November 8.”

## Open items and Gradescope readiness

No recorded pod list/count decision found. November 8, 2026 is a proposed
decision date supplied by Mohit, not an agreed resolution. GET /incidents or
formally revised ID-based criteria require pod decision; scope reduction needs
applicable instructor sign-off. Other specification issues: calendar support,
2025 extension, NOT_APPLICABLE days, duplicate handling, text limits and boundary
semantics. Owners: Srihari/calendar and Astha/API with both pod teams; Mohit
updates assertions only after agreement.

Q4.1–4.4, Q6.2, Q7.2 and Q8.1 are drafted with limitations in
[mohit-gradescope-draft.md](mohit-gradescope-draft.md). Q4.5 and Q6.1 need
actual deployed/reciprocal execution evidence; no local results substituted.
References are suggestions for Astha, not a rewritten shared submission.


## Final local rerun after reporting change

At 01:52:41 UTC, the database-backed non-acceptance rerun exited 0:
**324 passed, 93 deselected**, 11.08 seconds. The extra test is Mohit's AC-10
report mapping check; this explains the difference from Srihari's 323 count.
`uv run pytest tests/tester tests/fixtures -q`: 61 passed, exit 0.
Final Ruff format check after removing one extra blank line passes with 117
files; lint, mypy (74 files) and diff whitespace also pass. No requirement or
calendar expected date was relaxed. Local services were stopped after validation.
