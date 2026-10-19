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
