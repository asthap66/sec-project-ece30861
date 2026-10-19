# Phase 3 Gradescope answers: Q2, Q3, Q4 (paste-ready)

Q2 and Q3: Srihari. Q4: Mohit's content (`mohit-gradescope-ready.md`), fitted to the
Gradescope template. Compiled 2026-10-19. Cover-page version: `f551649`.

---

## Q2.1 Deployed web service

The service runs on Google Cloud Run in `us-central1` (project `ece30861-project-62ca4b`) as one Docker container: Python 3.12, FastAPI on Uvicorn, 1 vCPU and 512 MiB, behind Cloud Run's managed HTTPS at https://incident-api-356019173418.us-central1.run.app. Data lives in a separate Cloud SQL PostgreSQL 16 instance, so restarts and redeploys don't touch it. Each image is built in Cloud Build from a clean `git archive` of a commit, tagged with that commit, and every response carries an `X-App-Commit` header; the deployed version is `f551649` on the `integration` branch. A new version is released with `scripts/deploy_gcp.sh <git ref>`, which builds the image and rolls out a new Cloud Run revision; the container applies pending migrations (`alembic upgrade head`) before serving. The service is always on (minimum 1 instance, so no cold starts). Restrictions:
- Maximum 1 instance, because test-session coverage is kept in memory.
- Every endpoint except `GET /health` needs the shared key in `X-API-Key`, sent privately.
- `POST /reset` and `POST /test/setup` wipe the shared dataset, so podmates must agree a time window before destructive runs.
- It runs on our own free-trial billing, about $20–25/month, with a $50 budget alert. No other rate limits are set.

## Q2.2 Registry and team documentation

Registry entry: course class registry of deployed services, listing system https://incident-api-356019173418.us-central1.run.app and tester https://incident-tester-356019173418.us-central1.run.app │ Updated on: 2026-10-18

Team documentation: GitHub `asthap66/sec-project-ece30861`, branch `integration`:
- `README.md` and `docs/setup.md`: system overview and local setup
- `docs/deployment.md`: operations
- `docs/cross-team-testing.md`: testing interface and access
- `docs/incident-evidence.md`: incident and evidence interfaces
- `docs/models/`: models
- `docs/contract-issues.md`: open spec points
- `docs/submission/q7-status-and-limitations.md`: known limitations
- `docs/test-results/`: recorded runs

│ Updated on: 2026-10-19

## Q2.3 Operational experience supported by observability evidence

Our Phase 2 plan (pod spec Q5.3 with REQ-13 to REQ-15) was to deploy at our own HTTPS base URL, require the shared key in `X-API-Key`, keep data across restarts, and call `POST /reset` before each test run; all of this held in practice, except that shared resets turned out to need coordinating between teams. Persistent data is in Cloud SQL PostgreSQL, created by Alembic migrations at startup; `POST /reset` (API key required) truncates the evidence and incidents tables in one transaction and restarts IDs at INC-001/EVD-001. On deployment `f551649`, 100 incidents survived a restart into a new revision, and all were gone after reset (AC-16, 2026-10-19). The database URL and API key are stored in Google Secret Manager and injected as environment variables at start, never in git, images or logs; the key is compared in constant time, and a missing configured key rejects all requests. Our middleware writes one log line per request with a request ID, method, path, status, duration and record IDs (never headers or bodies) to Cloud Logging, and returns the ID in `X-Request-Id`, so a client failure can be matched to its line; 5xx counts and latency come from Cloud Run's request metrics. These logs are how we found that the other team's tester was resetting our database during our first AC-16 attempt (24 `POST /reset` calls from their IP during our create step).

Excerpt from the deployed service (`f551649`, Cloud Logging, 2026-10-19): health check, reset without a key, unknown incident, delete attempt, then the authenticated reset ending the AC-16 run:

```
2026-10-19 02:39:01,822 INFO app.requests request_id=6dde5bf9269f method=GET path=/health status=200 duration_ms=4.6 ids=-
2026-10-19 02:39:01,916 INFO app.requests request_id=e202b7a97d02 method=POST path=/reset status=401 duration_ms=0.6 ids=-
2026-10-19 02:39:02,024 INFO app.requests request_id=db1ddc6f5d47 method=GET path=/incidents/INC-999 status=404 duration_ms=26.3 ids=INC-999
2026-10-19 02:39:02,105 INFO app.requests request_id=c7a06a51278e method=DELETE path=/incidents/INC-001 status=405 duration_ms=1.1 ids=INC-001
2026-10-19 02:11:05,025 INFO app.requests request_id=ce7fdc2efe55 method=POST path=/reset status=200 duration_ms=37.4 ids=-
```

---

## Q3.1 Operation status

GET /health │ Requirement(s): REQ-13 │ Implemented: yes
Success responses conform: yes (`200 {"status": "OK"}`, no key needed) │ Error responses conform: yes (none defined)

POST /incidents │ Requirement(s): REQ-01, REQ-02 │ Implemented: yes
Success responses conform: yes (`201 {incidentId, status: "OPEN"}`) │ Error responses conform: yes (400 naming the field, 401). Title ≤ 200 and description ≤ 5,000 characters are provisional: Q5.2 says the maximum length is "agreed by both teams", and no value has been agreed yet.

POST /incidents/{incidentId}/evidence │ Requirement(s): REQ-03 │ Implemented: yes
Success responses conform: yes (`201 {evidenceId, recordedAt}`) │ Error responses conform: yes (400, 401, 404)

GET /incidents/{incidentId} │ Requirement(s): REQ-01, REQ-03, REQ-04, REQ-06 │ Implemented: partial
Success responses conform: yes (all contract fields returned; `currentDecision` and `filing` are always null until decisions and filings exist in Phase 4) │ Error responses conform: yes (401, 404)

POST /incidents/{incidentId}/decisions │ Requirement(s): REQ-04, REQ-05, REQ-08, REQ-09 │ Implemented: no (Phase 4)
Success responses conform: n/a │ Error responses conform: n/a (currently returns `404 {"error":"NOT_FOUND"}`, checked 2026-10-19; the same applies to the four operations below)

POST /incidents/{incidentId}/corrections │ Requirement(s): REQ-06, REQ-08, REQ-09 │ Implemented: no (Phase 4)
Success responses conform: n/a │ Error responses conform: n/a

GET /incidents/{incidentId}/deadline-status │ Requirement(s): REQ-09, REQ-10 │ Implemented: no (Phase 4)
Success responses conform: n/a │ Error responses conform: n/a

POST /incidents/{incidentId}/filing │ Requirement(s): REQ-08, REQ-11 │ Implemented: no (Phase 4)
Success responses conform: n/a │ Error responses conform: n/a

GET /incidents/{incidentId}/timeline │ Requirement(s): REQ-12 │ Implemented: no (Phase 4/5)
Success responses conform: n/a │ Error responses conform: n/a

POST /reset │ Requirement(s): REQ-14 │ Implemented: yes
Success responses conform: yes (`200 {"status": "RESET_COMPLETE"}`) │ Error responses conform: yes (401)

Cross-cutting, applied to every implemented operation:
- 401 for a missing or wrong `X-API-Key` (everything except `/health`).
- 405 for edit or delete attempts (append-only).
- Errors as `{"error": CODE, "message"}`.
- Request timestamps in RFC 3339 with an offset; responses in UTC.

Not part of the pod contract: the course testing interface (`POST /test/setup`, `GET /test/report`) is also deployed, and uses the course's `{message, source}` error format.

Integration: Every request first passes the request-logging middleware (request ID, timing, `X-App-Commit`), then the API-key middleware, which rejects bad keys before routing, so no validation or lookup runs without a key. The request is then routed to the system router (`/health`, `/reset`), the incident and evidence routers, or the testing-interface router. Pydantic schemas validate the body, with failures turned into contract 400s by shared error handlers, and route code reads and writes PostgreSQL through one SQLAlchemy session per request, with IDs generated by the database. Phase 3 added Astha's incident and evidence routers and schemas on top of the skeleton (config, database session, models and migrations, auth, errors, logging); the later testing-interface router reuses the same database and auth layers.

## Q3.2 Contract changes and pod communication

Contract version at delivery: v1.0 (Phase 2 pod specification, Sections 5.1–5.3, agreed at the pod meeting on Friday 25 September at 5 PM with both teams present, with no remaining disagreements recorded).

Changes since Phase 2: none. The contract was not changed in Phase 3.

Pod agreement: no change needed agreement. Open questions are tracked in `docs/contract-issues.md` and with the other team over our pod's chat channel. <!-- confirm the channel name -->

Intentional deviations and resolution plan: no deviation from a contract-defined behaviour. Two places where the contract is silent use our own provisional choices, and we will agree them with the other team before Phase 4 tests depend on them:
- **Field lengths:** Q5.2 leaves the title and description maximum to be "agreed by both teams" (REQ-02 rejects inputs that are too long), but no value has been agreed. We use 200 and 5,000 characters provisionally; the other team's schema sets no maximum.
- **Error codes:** `INVALID_<FIELD>`, `UNAUTHORIZED`, `NOT_FOUND`, `METHOD_NOT_ALLOWED`.

A proposed `GET /incidents` list operation (needed to count incidents in AC-02/AC-16) is not implemented and would be added only as a pod-agreed v1.1 change.

---

## Q4.1 Test runner and execution instructions

Base URL override: the acceptance suite reads the target from environment variables, with no change to test code: `BASE_URL=<any team's base URL> API_KEY=<that team's key> uv run pytest -m acceptance` (the key is sent as `X-API-Key`). Through the course interface, our deployed tester (https://incident-tester-356019173418.us-central1.run.app) takes the target in `POST /test/setup {"target_url": ...}`, and approved targets' keys come from Secret Manager.
│ Response received: `GET /health` → `200 {"status":"OK"}` without a key, and `X-App-Commit: f551649`; a missing or wrong key on `/incidents/...` → `401 {"error":"UNAUTHORIZED","message":"missing or invalid API key"}` (2026-10-19).
│ Conforms to spec: yes. No instructor OpenAPI file was available to our team, so conformance was checked against the Phase 2 pod contract v1.0, which the other team's published OpenAPI document also transcribes.
Known deviations from the OpenAPI spec: none for implemented operations. Notes:
- Title ≤ 200 and description ≤ 5,000 characters are provisional, because Q5.2 leaves the maximum to be agreed by both teams and none has been agreed yet.
- `HEAD /health` returns 405; only GET is specified.
- Phase 4 operations (decisions, corrections, deadline-status, filing, timeline) are not implemented yet.

## Q4.2 Tests for new functionality

AC-01 │ Requirement(s): REQ-01, REQ-14
Test(s): test_ac01_create_then_retrieve_returns_identical_values, test_ac01_each_incident_gets_a_distinct_id │ Type: success, boundary (timezone offsets, non-ASCII text) │ Automated: yes

AC-02 │ Requirement(s): REQ-02, REQ-14
Test(s): test_ac02_invalid_incident_is_rejected_naming_the_field, test_postgres_invalid_incidents_do_not_write │ Type: failure (missing or empty fields, malformed, offset-less or future timestamps, wrong types) │ Automated: yes. AC-02 expects "the incident count is unchanged", but the contract has no list operation, so the count is checked in the database test and over HTTP for known IDs. Maximum-length tests are pending the pod's agreement on limits.

AC-03 │ Requirement(s): REQ-14
Test(s): test_ac03_unknown_id_get_and_post_return_404, test_unknown_incident_get_is_404_with_error_format │ Type: failure │ Automated: yes

AC-04 │ Requirement(s): REQ-03
Test(s): test_ac04_three_technical_items_are_linked_to_the_incident, test_ac04_evidence_is_not_shared_between_incidents │ Type: success, failure │ Automated: yes

AC-05 │ Requirement(s): REQ-03
Test(s): test_ac05_evidence_is_stored_and_returned_unchanged, test_invalid_evidence_is_rejected_and_not_attached │ Type: success (all four categories), failure (bad category, missing field, bad timestamp) │ Automated: yes

AC-08 (partial: no-edit/no-delete only) │ Requirement(s): REQ-07
Test(s): test_stored_incident_cannot_be_edited_or_deleted │ Type: failure (PUT/PATCH/DELETE → 405, record unchanged) │ Automated: yes. Correction history is Phase 4.

AC-14 │ Requirement(s): REQ-13
Test(s): test_health_is_public, test_authenticated_route_rejects_bad_key, test_authenticated_route_accepts_valid_key, test_deployment_uses_https │ Type: success, failure │ Automated: partly. The pod spec has AC-14 combine automated tests with a code/deployment inspection, which the other team does with a checklist during cross-team testing.

AC-16 │ Requirement(s): REQ-14, REQ-15
Test(s): test_reset_requires_key, test_reset_succeeds_and_is_repeatable, scripts/check_persistence.py (create → restart → verify → reset), scripts/performance.py (100 incidents loaded, 200 timed requests, ≥ 95% within 1 s) │ Type: success, failure, performance threshold │ Automated: yes. Only the restart between the persistence steps is run by hand (a new Cloud Run revision).

Every core operation has at least one failure-path test:
- POST /incidents: AC-02
- GET /incidents/{id}: AC-03
- POST /evidence: AC-03 (unknown parent) and AC-05
- /reset: test_reset_requires_key

Oracles: The expected outputs were taken directly from the pod contract v1.0 (status codes, response fields, ID and UTC timestamp formats) and stored next to the synthetic inputs in shared JSON fixtures, so they're defined independently of either implementation. We trust them because the same fixtures pass against both teams' independent implementations, and because the suite catches missing behaviour: 33 of 35 incident and evidence tests failed against a build without those routes. The two that still passed were the unknown-ID checks, which correctly expect 404.

## Q4.3 Regression and static checks

GitHub Actions reruns every existing test on every pull request and every push to `main` or `integration`. It:
- runs the 212 unit and infrastructure tests against a disposable PostgreSQL,
- starts the application and runs all 48 acceptance tests against it over HTTP,
- creates 100 incidents, restarts the app, checks persistence, and runs the response-time check.

Phase 4 changes are therefore checked against all the Phase 3 behaviour before merging, and the same acceptance suite is rerun against both deployed systems through the testers. On the deployed commit, all non-acceptance tests passed. The CI acceptance run had 47 passes and one expected skip, because the CI service is local HTTP, not HTTPS.

CI run: https://github.com/asthap66/sec-project-ece30861/actions/runs/39182054445

## Q4.4 Static checks

Ruff linting, Ruff format checking and strict mypy type checking run in CI before the tests, on every pull request and every push to `main` or `integration`; all three passed for deployed commit `f551649`. A failing check does not automatically block a merge or deployment: branch protection is not enabled, and deployment is a manual script. Blocking is a team practice (we review CI results before merging and deploying), not an enforced gate.

CI run: https://github.com/asthap66/sec-project-ece30861/actions/runs/39182054445

## Q4.5 Test results against the deployed system

Run date/time: 2026-10-18 (acceptance suite through our deployed tester); 2026-10-19 02:10–02:11 UTC (AC-16 persistence and performance) │ Version tested: `f551649`
Tests run: 48 │ Passed: 48 │ Failed: 0 │ Skipped: 0

AC-16 scripts on the same version:
- Persistence: 100/100 incidents intact after restarting into a new revision.
- Performance: 200/200 requests within 1 s, 0 errors (p50 46 ms, p95 65 ms, max 172 ms).
- Reset: 100/100 created incidents gone after `POST /reset`.

Tester coverage: code 135/522 app lines; component null (the pod spec defines no components); system 8/16 ACs exercised. Exercised doesn't mean fully satisfied: AC-08 and AC-16 are partial in the suite.

Failure: none in the reported runs. An earlier AC-16 attempt (02:08 UTC) found 92/100 incidents intact.
│ Classification: test (environment), not system │ Cause: the other team's tester was running a session against our service at the same time, and Cloud Run logs show 24 `POST /reset` calls from their IP during our create step │ Plan: separate destructive-test windows agreed with the other team (Phase 4); the isolated rerun passed, and both attempts are recorded in `docs/test-results/2026-10-19-ac16-deployed.md`.

---

## Q8.1 Actual GenAI use (Srihari)

Tools and delegation: I used Claude Code in the terminal, on my own branches, to write code and documentation for the infrastructure, database and deployment work, in line with our Phase 2 plan of using GenAI for development but not inside the running system. The design decisions and their tradeoffs were mine; the tool mostly produced options and implementations for me to choose between and check.

What I delegated:
- the FastAPI skeleton: config, SQLAlchemy models and Alembic migrations, API-key middleware, error handlers, request logging
- Docker and deployment scripts
- the course testing interface and our separate tester service
- infrastructure tests and first drafts of my docs

Decisions I made:
- **Hosting:** Google Cloud Run with Cloud SQL rather than AWS, because a managed container plus managed PostgreSQL was the least operations work for a three-person team. I put it in a new project on its own billing account with a $50 budget alert, so course costs stay separate from other accounts.
- **Always on:** one instance kept warm, about $20–25/month, instead of scale-to-zero, so REQ-15's 1-second target never hits a cold start.
- **Single instance:** a cap of one instance, trading scalability for correct per-session coverage reports, since coverage is held in memory.
- **Secrets and access:** keys in Secret Manager and shared only by private message.
- **Branches:** separate `infra` and `integration` branches, merging to `main` only through a reviewed pull request.
- **Cross-team testing:** letting the other team's tester reset our system.

Verification: Nothing was merged until Ruff, strict mypy and the full test suite (212 unit/infrastructure tests plus 48 acceptance tests) passed locally and in CI, and I re-ran the suite on a fresh clone of the integration branch before deploying. I checked deployed behaviour directly instead of trusting generated summaries:
- the `X-App-Commit` header to confirm the running version
- live 401/404/405 responses
- Cloud Logging for the matching request lines
- the AC-16 persistence and performance scripts against the deployment

I also checked submission claims against the Phase 2 pod document. That caught a draft that said the contract sets no field-length limit, when Q5.2 says the limit is to be agreed by both teams.

Correction example: While setting up Cloud SQL, a generated zsh command wrote the project variable as `$P:us-central1`. zsh reads `:u` as an "uppercase" modifier, so the stored database URL secret and the proxy connection name came out with an uppercased project ID. I caught it when the Cloud SQL proxy could not find the instance. I fixed it by using `${P}`, adding a corrected secret version and disabling the bad one, then confirmed with a successful database connection and deployment. A second example: the first AC-16 run reported only 92/100 incidents intact. Instead of accepting a persistence defect, I checked the Cloud Run logs, which showed the other team's tester sending 24 resets during our run. We recorded it as test interference and re-ran in an isolated window.

Agentic principles: I mostly followed them. I set the scope and constraints for each task (no secrets in the repo or logs, never push to `main`, destructive tests only against our own synthetic data), and I accepted output only after an objective check: tests, static analysis, and live HTTP and log evidence. When the tool proposed options, I made the call based on our requirements and constraints instead of taking its default. For example, I chose the second Cloud Run service for the tester, and I chose to coordinate with the other team before they reset our system.

I deviated in places, honestly:
- I let the agent run long multi-step sequences on its own, including deployments and cloud configuration, and reviewed the results afterwards rather than each step.
- Its commits are under my name, with this section as the disclosure.
- I started the first AC-16 run without first agreeing a test window with the other team, which caused the interference above.
