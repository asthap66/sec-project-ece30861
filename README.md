# Phase 3: Team Implementation and Responsibility Plan

> **Repository status:** Initial scaffold only. Business endpoints, authentication, database models/migrations, and deployment are not implemented yet.
>
> For local setup, dependency installation, running the app, and running checks, see [docs/setup.md](docs/setup.md).

Team: Srihari, Astha, Mohit

This is a work plan, not a claim that implementation or testing is complete. File paths and branch names below are proposed conventions; adapt them to the actual repository. Confirm the instructor-provided OpenAPI specification before coding. No repository, deployed URL, or final submission deadline has been supplied for this plan.

## 1. Goal and scope

Deliver an authenticated, persistent, deployed JSON HTTP API that creates/retrieves cybersecurity incidents and attaches evidence. Follow the Phase 2 milestone in Section 6.1: REQ-01, REQ-02, REQ-03, REQ-13, and applicable portions of REQ-14 and REQ-15.

Phase 3 endpoints:

| Operation | Owner | Required outcome |
| --- | --- | --- |
| GET /health | Srihari | Public health response |
| POST /reset | Srihari | Authenticated reset of synthetic test data |
| POST /incidents | Astha | Validate, persist, return 201 with incident ID and OPEN status |
| GET /incidents/{incidentId} | Astha | Retrieve incident and its evidence; unknown ID returns 404 |
| POST /incidents/{incidentId}/evidence | Astha | Validate, link evidence, persist, return 201 |

Materiality decisions, corrections, deadlines, filings, and full timeline reporting remain later-phase work. No frontend is planned for this increment. Document all contract operations in the submission, including those not yet implemented.

## 2. Ownership summary

| Person | Primary responsibility | Branch | Submission lead |
| --- | --- | --- | --- |
| Srihari | App infrastructure, database, security, deployment | infra | Q2 and Q3 |
| Astha | Incident/evidence features and feature tests | incident-evidence | Q1 and Q5 |
| Mohit | Acceptance-test code, CI, validation, cross-team coordination | acceptance-ci | Q4 and Q6 |

Everyone reviews code, fixes bugs in their own area, and contributes to Q7-Q9. Mohit owns the validation framework, not every test or every bug fix.

## 3. Srihari: infrastructure and deployment

### Coding checklist

- [ ] Initialize FastAPI application and register routers.
- [ ] Own dependency configuration and coordinate package additions from teammates.
- [ ] Implement configuration for DATABASE_URL and API_KEY; provide .env.example with placeholders only.
- [ ] Configure PostgreSQL connection/session lifecycle.
- [ ] Define Incident and Evidence models and initial database migration with Astha's input.
- [ ] Add foreign-key relationships and transactional writes/reset behavior.
- [ ] Provide get_db() for route/service database access.
- [ ] Implement require_api_key(); reject missing/wrong X-API-Key with the agreed 401 JSON response.
- [ ] Keep GET /health public. Apply authentication to every other contract endpoint.
- [ ] Implement POST /reset, clearing dependent evidence before incidents in one transaction.
- [ ] Implement shared error helpers and handlers, including mapping request-validation failures to the contract's 400 response rather than framework-default behavior.
- [ ] Handle agreed 404/405 errors consistently; do not invent responses for future operations.
- [ ] Add request logs: method, path, status, duration, and incident/error identifiers when available. Never log secrets or full incident bodies.
- [ ] Create Docker/local database configuration and deploy over HTTPS using the agreed host.
- [ ] Verify database persistence across app restarts with Mohit.
- [ ] Add focused infrastructure tests for authentication, health, reset, and error helpers.

### Proposed file ownership

`app/main.py`, `app/config.py`, `app/db.py`, `app/models.py`, `app/auth.py`, `app/errors.py`, `app/routes/system.py`, `migrations/`, `Dockerfile`, `compose.yaml`, `.env.example`, dependency files, `tests/infrastructure/`.

### Initial database fields

- Incident: internal ID, title, description, discovered_at, reporter_name, created_at.
- Evidence: internal ID, incident foreign key, category, summary, source, collected_at, recorded_at.
- Persist timezone-aware timestamps. Generate public IDs in the agreed format; do not assume the example IDs mandate a sequence.
- Phase 3 incidents remain OPEN. Preserve the Phase 2 design of deriving status from decisions/filings when those features are added.

### Handoff and completion

First handoff: runnable skeleton, model fields, database dependency, error-helper signature, and authentication dependency. Share these before Astha connects routes. Later handoff: deployed base URL, secret-sharing instructions, deployment commit, restart procedure, and a sanitized log excerpt. Done when the service is reachable, auth/reset work, and data survives an application restart.

## 4. Astha: incident and evidence functionality

### Coding checklist

- [ ] Define request/response schemas matching the agreed OpenAPI contract, including camelCase JSON field names.
- [ ] Implement POST /incidents: required-field validation, agreed length limits, timezone-aware discovery timestamp, no future discovery time, persistence, and 201 response.
- [ ] Implement GET /incidents/{incidentId}: retrieve the incident with its evidence and required null fields such as currentDecision/filing if specified by the contract.
- [ ] Implement POST /incidents/{incidentId}/evidence: validate parent existence, category, summary/source, and timestamp format; generate evidence ID and recordedAt on the server.
- [ ] Accept the four agreed categories: TECHNICAL, BUSINESS_IMPACT, LEGAL, OTHER.
- [ ] Normalize response timestamps to UTC and retain the submitted instant.
- [ ] Use Srihari's database/auth/error interfaces instead of creating separate versions.
- [ ] Ensure invalid requests leave no partial records in the database.
- [ ] Add feature tests for valid inputs, missing/empty fields, agreed length boundaries, timestamp validation, invalid categories, and unknown IDs.
- [ ] Update incident/evidence information models and request-flow documentation to match the implemented system.

### Proposed file ownership

`app/schemas.py`, `app/routes/incidents.py`, `app/routes/evidence.py`, `app/services/incidents.py`, `app/services/evidence.py`, `tests/unit/`, `docs/models/`.

### Handoff and completion

Provide working request/response examples, route PRs, feature-test results, and a list of known limitations to Mohit. Done when create -> retrieve -> attach evidence -> retrieve succeeds and invalid inputs return contract-compliant errors without changing data.

## 5. Mohit: automated validation, CI, and cross-team testing

### Coding checklist

- [ ] Build a reusable HTTP test client configured by BASE_URL and API_KEY; never hardcode deployed URLs or credentials.
- [ ] Add synthetic fixtures using safe historical discovery timestamps and a clearly future timestamp for rejection tests.
- [ ] Implement acceptance tests for AC-01 through AC-04 and AC-05 where supported by the evidence increment.
- [ ] Implement AC-14 checks: absent/wrong/valid API key, public health, and HTTPS deployment verification.
- [ ] Implement applicable AC-16 checks: reset, restart persistence, and response time.
- [ ] Assert response status codes, required fields, types, error format, timestamp behavior, and evidence-to-incident linkage.
- [ ] Include success, failure, and boundary cases for each delivered core operation.
- [ ] Verify rejected writes do not change state using supported observations; resolve the missing list-endpoint ambiguity before relying on GET /incidents.
- [ ] Create a performance script that loads 100 synthetic incidents and times 200 requests; report the proportion under one second and the test conditions.
- [ ] Coordinate a persistence test with Srihari: create data, restart the application without reset, retrieve the same data, then test reset separately.
- [ ] Configure GitHub Actions to run Ruff, mypy, and local tests with a disposable PostgreSQL service. Coordinate required-check settings with the repository administrator.
- [ ] Keep destructive reset-based deployed tests explicit and restricted to the agreed synthetic test service; serialize runs with the other team.
- [ ] Run the complete current suite against the deployed version and record commit/tag, date, totals, failures, and skips.
- [ ] Run tests against the other team's service and arrange for their tests to run against ours. Record both directions and issue owners.
- [ ] Maintain requirement/test and operation-status tables for the submission, clearly marking future work unimplemented.

### Proposed file ownership

`tests/acceptance/`, `tests/conftest.py`, `tests/fixtures/`, `scripts/performance.py`, `scripts/check_persistence.py` (or documented manual restart step), `.github/workflows/ci.yml`, lint/type/test configuration, `docs/test-results/`, `docs/contract-issues.md`.

### Handoff and completion

Give Srihari/Astha reproducible requests for every failure, including expected versus actual results. Done when CI runs, deployed results are recorded, both cross-team testing directions are attempted, and failures are explained rather than hidden. Q4.1's OpenAPI-based instruction does not eliminate Q4.2-Q4.5 testing obligations.

## 6. Shared interfaces and decisions before coding

Hold one short kickoff and record:

1. Instructor-provided OpenAPI file/version and how it relates to the Phase 2 contract; resolve conflicts through the pod/instructor as appropriate.
2. Exact field limits, whitespace policy, timestamp rules, ID format, and error code/message expectations.
3. Whether GET /incidents exists: AC-02 mentions listing incidents but the Phase 2 interface table omits that route.
4. Database model fields and get_db() interface, owned by Srihari with Astha's review.
5. Shared API error helper signature and validation/authentication precedence.
6. Test API-key exchange, reset windows, and access to both deployments.

Do not silently change the common contract or reduce the agreed scope. Record changes and pod agreement. Avoid adding extra evidence timestamp restrictions that are absent from the agreed specification.

## 7. Integration sequence

| Milestone | Srihari | Astha | Mohit | Exit condition |
| --- | --- | --- | --- | --- |
| A: Contract kickoff | Agree DB/auth/error interfaces | Agree schemas | Agree test expectations | Shared decisions recorded |
| B: Skeleton | App, DB, migrations, health, initial deployment | Schemas and validation | HTTP client, fixtures, initial tests | Runnable skeleton merged |
| C: First workflow | Auth and deployment integration | Incident create/retrieve | AC-01/02/03 and auth tests | Deployed create/retrieve works |
| D: Evidence | Reset and logging | Evidence endpoint and feature tests | Evidence/reset checks, CI | Full Phase 3 workflow works |
| E: Verification | Restart and operational evidence | Fix feature defects, update models | Persistence/performance and cross-team runs | Results and limitations recorded |
| F: Submission | Q2/Q3 and registry details | Q1/Q5 | Q4/Q6 and result tables | All members review Q1-Q9 |

No calendar dates are assumed. Agree dates for these milestones once the actual submission deadline is confirmed. Reserve a final shared session for deployed verification and submission review.

## 8. Git and collaboration rules

- Work on the assigned branches; submit small pull requests into main.
- Srihari coordinates app/model/dependency changes; Astha coordinates feature schemas/routes; Mohit coordinates test/CI configuration.
- Tell the file owner before changing shared files. Resolve interface disagreements before merging.
- Each PR describes behavior changed, tests run, and remaining limitations.
- Another teammate reviews each PR. Suggested rotation: Astha reviews Srihari, Mohit reviews Astha, Srihari reviews Mohit.
- Keep main deployable and run required checks before merge.
- Fix defects in the owning component; testing ownership does not transfer implementation bugs to Mohit.
- Keep credentials out of git, screenshots, logs, and report text.
- Cross-team coordination shares contracts, fixtures, and test results; each team maintains its independent implementation.

## 9. Submission ownership and evidence

| Section | Lead | Evidence |
| --- | --- | --- |
| Q1 Delivered increment | Astha | Capability description, REQ/AC status, comparison with Phase 2 |
| Q2 Deployment and operation | Srihari | Host/runtime, URL, commit mapping, secrets/persistence, sanitized log excerpt, registry/docs locations |
| Q3 Interface conformance | Srihari | Every contract operation marked yes/partial/no; Astha supplies feature details and Mohit supplies test results |
| Q4 Automated validation | Mohit | Test mappings, CI/static checks, deployed run results, failure explanations |
| Q5 Updated models | Astha | Current diagrams and implementation consistency checks; Srihari reviews architecture/storage |
| Q6 Cross-team readiness | Mohit | Both testing directions, specification ambiguities, pod decisions |
| Q7 Status and limitations | All; Mohit consolidates | Changes, unfinished scope, defects, Phase 4 adjustments |
| Q8 Actual GenAI use | All | Tools used, verification, real correction example, honest workflow reflection |
| Q9 References | All; Astha consolidates | Sources actually used, consistent numbering, citations |

Record real observations only. Do not claim successful deployment, CI, cross-testing, model corrections, or AI correction examples before they occur.

## 10. Final completion checklist

- [ ] Shared contract decisions recorded and reflected in implementation/tests.
- [ ] Deployed HTTPS health endpoint reachable.
- [ ] Authentication enforced on all other delivered endpoints.
- [ ] Incident creation/retrieval and evidence attachment work.
- [ ] Contract-compliant errors and UTC timestamps verified.
- [ ] Reset and restart persistence verified.
- [ ] Automated/static checks run; results tied to deployed commit/tag.
- [ ] Performance results recorded against the agreed threshold.
- [ ] Both directions of cross-team testing attempted and documented.
- [ ] Models, registry, project documentation, and operation-status table updated.
- [ ] Known limitations and future features explicitly listed.
- [ ] Every member reviews the final submission.

## Planning sources

- Phase 2 - Pod.pdf: requirements, acceptance criteria, common API contract, Phase 3 milestone in Section 6.1.
- Phase 2 Part 2.pdf: architecture decisions, operations, testing, reuse, AI use, and risks.
- Phase 3 submission screenshots dated October 16, 2026: Q1-Q9 evidence and reporting expectations.

This README assigns future work; it does not replace the instructor's OpenAPI contract or the pod's agreed specification.
