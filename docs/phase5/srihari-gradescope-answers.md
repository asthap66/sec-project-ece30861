# Phase 5 Gradescope answers: Srihari (Q2.1, Q2.3, Q5.1, Q5.2, Q7.2, Q8.1)

Drafted 2026-11-22 (Eastern) from observed evidence at `integration` `edb3573`.
Times are UTC unless marked ET. Nothing here is labelled fixed; open items stay
open until new test evidence exists.

---

## Q2.1 Deployed web service

The API runs on Google Cloud Run (service `incident-api`, project
`ece30861-project-62ca4b`, region `us-central1`, Python 3.12 container,
1 vCPU / 512 MiB) with its data in Cloud SQL PostgreSQL 16 (`incident-db`,
db-f1-micro) [1][2]. The Phase 5 release is revision `incident-api-00010-srt`
(created 2026-11-23T01:09:57Z = Nov 22, 8:09 PM ET), built from `integration`
commit `edb35739a215d732d9a5b9445bed4c71a07dd28e`; the image is tagged
`api:edb3573` and every response carries `X-App-Commit: edb3573`, so the
running version maps directly to a commit. A release is
`PROJECT_ID=ece30861-project-62ca4b scripts/deploy_gcp.sh <git-ref>`: Cloud
Build builds a clean `git archive` of the ref (no local files), Cloud Run rolls
out a new revision, and the container runs `alembic upgrade head` before
serving; rollback is routing traffic back to the previous revision
(`incident-api-00009-qdt`) [1][3]. The service is always on (min = max = 1
instance, no cold start); the single instance is deliberate because test-session
coverage is kept in memory, the shared database means podmates must use agreed
reset windows (`POST /reset` clears all data), every project route needs the
shared `X-API-Key`, and the project runs on free-trial credit (about $20–25 per
month, $50 budget alert), with no extra rate limit beyond Cloud Run defaults.

- API: https://incident-api-356019173418.us-central1.run.app │ revision `incident-api-00010-srt` │ SHA `edb3573`
- Tester: https://incident-tester-356019173418.us-central1.run.app │ revision `incident-tester-00007-cth` (created 2026-11-23T01:11:47Z) │ SHA `edb3573`

## Q2.3 Operational experience supported by observability evidence

The Phase 2 plan held: all data is in Cloud SQL, so restarts and new revisions
never touch it, and schema changes ship as Alembic migrations applied at
container start; migration `0004` (filings and decision corrections) ran on the
Phase 5 revision at 2026-11-23T01:10:08Z, and the AC-16 check verified 100/100
incidents intact across an app restart in CI. Reset is `POST /reset` (and
`/test/setup`), one `TRUNCATE ... RESTART IDENTITY` over all project tables,
now including `filings`; it clears all data as REQ-14 states, not only
synthetic records, so the pod used an exclusive window (Nov 22, 8:30–9:30 PM ET)
for deployed and reciprocal runs. Secrets (`api-key`, `database-url`) live only
in Google Secret Manager and are injected as environment variables at start;
none are in the repository, images or logs [4]. Failures are detected from one
structured `app.requests` log line per request (request ID, method, path,
status, duration, incident IDs; never keys or bodies) in Cloud Logging, plus
Cloud Run error logs [5]: on revision 00010, 1,544 requests between
01:10:31Z and 01:33:17Z had 0 responses ≥ 500 and 0 ERROR-severity entries, with
p50 45 ms, p95 83 ms and maximum 919 ms (none over 1 s, REQ-15).

```
2026-11-23 01:32:51,726 INFO app.requests request_id=c337ca7a39fb method=POST path=/incidents/INC-001/filing status=201 duration_ms=51.6 ids=INC-001
2026-11-23 01:32:51,898 INFO app.requests request_id=b17e9e5e3dad method=GET path=/incidents/INC-001/timeline status=200 duration_ms=56.8 ids=INC-001
2026-11-23 01:10:08 INFO [alembic.runtime.migration] Running upgrade 0003 -> 0004, Add filings and decision corrections (Phase 5).
Revision incident-api-00010-srt status counts: 200×595, 201×744, 400×135, 401×28, 404×24, 405×7, 409×11, 5xx×0
```

## Q5.1 Model updates

All updated diagrams are in `docs/models/phase5-storage-workflow.md` (sections
noted), drawn from the code at `edb3573`; the Phase 4 files remain as history.

- **Database model (ER, Phase 2 Model 2 / Phase 4 §1)** │ Changed: yes │ Added `filings` (one per incident, timeliness stored as classified), `decisions.corrects_decision_id` (unique, same-incident link), recording times from `clock_timestamp()`, reset includes `filings`; needed for filing, append-only corrections and a trustworthy timeline order │ Location: §1
- **Incident state machine (Phase 4 decisions model)** │ Changed: yes │ Added correction transitions and the terminal FILED state (decision, correction and filing all 409 after FILED); this is what `decision_status()` and `Phase5Service` implement │ Location: §2
- **Write transaction (sequence, Phase 4 §2)** │ Changed: yes │ Same lock → validate → append → single commit/rollback, now with `append_correction` and `append_filing` and the calendar classifying timeliness │ Location: §3
- **Timeline read (sequence)** │ Changed: new │ Shared lock for a consistent snapshot, recording-time order, evidence counts and duration rule │ Location: §4
- **Validation order (Phase 2 Model 4)** │ Changed: no (spec) │ Added a table comparing each route's implemented order with Model 4; corrections/filing currently differ │ Location: §5
- **Deadline model (Phase 2 Model 3 / Phase 4 §3)** │ Changed: no │ Filing timeliness reuses the same calendar (Eastern date, 4th business day, `us-federal-2025-2027.v1`) │ Location: Phase 4 file §3
- **Deployment model (Phase 2 §7.1 / Phase 4 §4)** │ Changed: no (architecture) │ Same components; revisions, image tags and migration head updated; Cloud SQL backups noted as off │ Location: §6

## Q5.2 Model–implementation consistency

The Phase 5 models were written from the implementation rather than the plan:
each table, column and constraint was traced to `app/models.py` and migration
`0004`, each transition to `decision_status()` and `Phase5Service`, and each
deployment value to `gcloud run revisions describe` and the live
`X-App-Commit` header at revision 00010; the behavior each model claims is also
asserted by tests (31 PostgreSQL tests in `tests/infrastructure/test_phase5_database.py`
and Mohit's 34 Phase 5 HTTP tests, 127/127 against the deployed API). Two
divergences were resolved by **correcting the model**: Phase 2 Model 2 named
filing fields `filing_date`/`filed_by`, while the shared contract and the code
use `filedAt`/`accessionNumber` (no `filedBy` stored), and the Phase 4 model
showed recording times as `now()`, which the implementation deliberately changed
to `clock_timestamp()` so a request waiting on the incident lock cannot be
stamped before the write it waited behind. One divergence will be resolved by
**correcting the code**: Phase 2 Model 4 requires incident existence before
body validation, but the Phase 5 correction and filing routes parse the body
first (400 instead of 404 for a malformed body on an unknown incident, found by
the other pod's tester); §5 records it and Astha owns the fix.

## Q7.2 Known limitations and defects

Observed at `edb3573` / `incident-api-00010-srt` unless noted. Defects vs open
policies are labelled.

- **LIM-01** │ Defect: correction and filing validate the body before checking the incident, so a malformed body on an unknown incident returns 400, not 404 (Model 4 order) │ Affects: `POST /incidents/{id}/corrections`, `POST /incidents/{id}/filing` │ Severity: medium
  Workaround for podmates: send a well-formed body when testing unknown incidents │ Target phase: 6 (owner Astha)
- **LIM-02** │ Defect: `deadline-status` ignores the filing, so a FILED incident still reports PENDING/OVERDUE (e.g. OVERDUE 10 after an on-time filing) instead of NOT_APPLICABLE │ Affects: `GET /incidents/{id}/deadline-status` │ Severity: medium
  Workaround: read `status` and `filing.timeliness` from `GET /incidents/{id}` │ Target phase: 6 (owner Astha)
- **LIM-03** │ Open specification: business days late for a filing on the weekend right after the deadline: we return LATE with 0, the other pod expects 1 │ Affects: `POST /incidents/{id}/filing` (businessDaysLate) │ Severity: low
  Workaround: assert `timeliness` only for weekend filings │ Target phase: 6 (owner Srihari, needs both pods)
- **LIM-04** │ Open specification: `discoveryToDeterminationDays` is exact elapsed days (2 decimals, e.g. 6.81); the other pod expects whole days (7) │ Affects: `GET /incidents/{id}/timeline` │ Severity: low
  Workaround: compare with a tolerance or rounded │ Target phase: 6 (owner Srihari, needs both pods)
- **LIM-05** │ Open policy: a filing dated before the determination, or in the future, is accepted and classified (ON_TIME) │ Affects: `POST /incidents/{id}/filing` │ Severity: medium
  Workaround: none; do not rely on it being rejected │ Target phase: 6 (owner Astha)
- **LIM-06** │ Open policy: a stale or unknown `correctsDecisionId` returns 400; the contract doesn't say 400 or 409 │ Affects: corrections │ Severity: low
  Workaround: accept 400 or 409 │ Target phase: 6 (owner Astha)
- **LIM-07** │ Limitation: reset clears all data (REQ-14), not only synthetic records; the deployment is shared │ Affects: `POST /reset`, `/test/setup` │ Severity: medium
  Workaround: run destructive tests only in an agreed exclusive window │ Target phase: 6 (pod decision)
- **LIM-08** │ Limitation: deadline and timeliness calculations cover 2025–2027 only; other dates return 400 `DATE_OUT_OF_RANGE` │ Affects: decisions, corrections, filing, deadline-status │ Severity: low
  Workaround: use 2025–2027 dates │ Target phase: 6 if a holiday list is extended
- **LIM-09** │ Limitation: no incident-list endpoint, so AC-02's count check is skipped │ Affects: AC-02 │ Severity: low
  Workaround: re-GET created IDs │ Target phase: 6 (pod decision)
- **LIM-10** │ Operational: one Cloud Run instance on a db-f1-micro database; only observed load measured (1,544 requests, p95 83 ms), no stress test │ Affects: all operations │ Severity: low
  Workaround: avoid parallel bulk runs during another team's window │ Target phase: 6
- **LIM-11** │ Operational: Cloud SQL automatic backups are off; an instance failure would lose stored data │ Affects: persistence │ Severity: low (synthetic data only)
  Workaround: none needed for synthetic data │ Target phase: 6 (enable if real data)
- **LIM-12** │ Operational: downgrading migration `0004` drops filings and correction links │ Affects: rollback below Phase 5 │ Severity: low
  Workaround: roll back the revision, not the schema │ Target phase: none planned

## Q8.1 Actual GenAI use (Srihari, first person; edit before submitting)

**Tools and delegation.** I used Claude Code (Anthropic's coding agent) for my
Phase 5 part. I gave it Astha's API handoff, Mohit's Phase 5 plan and his
acceptance branch, and delegated the implementation: the SQLAlchemy Phase 5
repository, migration `0004`, the PostgreSQL tests, the handoff note, these
model diagrams and the Q2/Q5/Q7.2 drafts; I also had it run the deployment
scripts and collect the deployment evidence. I chose the scope, the branch
and merge steps and what to send to the team.

**Verification.** Nothing was accepted on the agent's word: every change was run
against a real PostgreSQL 16 database (371 local tests, including concurrency
tests repeated 15 times), Mohit's independently written acceptance tests were
run unchanged over HTTP against my branch (34/34), the CI workflow was replayed
on a trial merge before merging, and after deployment I checked the live
`X-App-Commit` header, the migration log line and non-destructive requests.
The model diagrams were checked against the code and the live revision, and
numbers in these answers come from Cloud Logging and `gcloud` output.

**Correction example.** One of the agent's own tests expected
`discoveryToDeterminationDays` of 2099.54 for the fixture incident; the test
failed against the database. Recomputing by hand (discovered 2020-01-01 14:00Z,
determined 2025-09-30 13:00Z: 2,099 days minus one hour = 2098.96) showed the
implementation was right and the test's expected value was wrong, so the
oracle was fixed, not the code. Probing edge cases also surfaced the
deadline-status-after-filing defect, which I flagged to Astha rather than
having the agent change her service.

**Agentic principles.** I followed the parts about independent oracles and
evidence: acceptance came from Mohit's tests and the shared contract, not from
tests the agent wrote for its own code, and open contract questions were left
to the pod instead of being decided in code. Honestly, I deviated on review
depth: I reviewed results, tests and diffs at a summary level rather than line
by line, and I let the agent run the merge into `integration` and the
deployment on my instruction, relying on CI and the checks above instead of a
separate human review before release.

## References (for Q9; numbers to be merged with the team list)

[1] Google Cloud. "Cloud Run documentation: Deploying container images / Managing revisions." https://cloud.google.com/run/docs. Accessed: 2026-11-22.
[2] Google Cloud. "Cloud SQL for PostgreSQL documentation." https://cloud.google.com/sql/docs/postgres. Accessed: 2026-11-22.
[3] SQLAlchemy project. "Alembic documentation: Tutorial and operation reference." https://alembic.sqlalchemy.org/. Accessed: 2026-11-22.
[4] Google Cloud. "Secret Manager: Using secrets with Cloud Run." https://cloud.google.com/run/docs/configuring/services/secrets. Accessed: 2026-11-22.
[5] Google Cloud. "Cloud Logging: Viewing logs for Cloud Run." https://cloud.google.com/run/docs/logging. Accessed: 2026-11-22.
[6] PostgreSQL Global Development Group. "Date/Time Functions: clock_timestamp()." PostgreSQL 16 documentation, Section 9.9.5. https://www.postgresql.org/docs/16/functions-datetime.html. Accessed: 2026-11-22.
