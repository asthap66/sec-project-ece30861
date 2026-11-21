# ECE 30861 Phase 5 Work Plan

## Purpose

Phase 5 must deliver the next coherent increment of the SEC Cybersecurity Disclosure System. The system must remain deployable, testable, and compatible with the shared interface. The work should extend the Phase 4 materiality-decision and deadline workflow with filing, correction, and history capabilities that were previously deferred.

The pod has three members:

- **Astha:** API, request validation, and contract-facing behavior
- **Srihari:** persistence, migrations, calendar/deadline integration, and deployment
- **Mohit:** automated testing, regression protection, CI evidence, integration verification, and documentation

No person should merge another person’s work without reviewing the related tests and contract behavior.

## Phase 5 target increment

The recommended Phase 5 increment is:

1. Allow authorized users to submit or record a filing for an incident.
2. Apply filing-state transitions after a MATERIAL decision.
3. Classify filing timeliness, including ON_TIME and LATE behavior.
4. Support decision corrections while preserving the append-only history.
5. Expose incident decision, evidence, correction, and filing history through the timeline operation.
6. Resolve or explicitly document the remaining shared contract questions before final submission.

The final scope must be checked against the instructor’s Phase 2 Section 6.3 milestone and the current shared OpenAPI specification before implementation begins. If the pod changes shared scope, both teams must agree and obtain any required instructor approval.

## Shared rules before coding

- Work from a clean `integration` branch.
- Create one branch per person:
  - `phase5/astha-api`
  - `phase5/srihari-storage-calendar`
  - `phase5/mohit-tests-docs`
- Do not commit credentials, API keys, database URLs, or private deployment values.
- Do not silently change the common interface contract.
- Every new route must have success, validation, authentication, unknown-resource, and state-conflict tests.
- Every database change must include a migration and restart/reset verification.
- Expected test values must come from independent fixtures or the written specification, not from the production implementation being tested.
- Keep Phase 3 and Phase 4 tests running as regression tests.
- Use synthetic incidents and an agreed reset procedure for deployed testing.
- Record unresolved behavior as a limitation rather than weakening an assertion.

## Astha: API and contract behavior

### Primary responsibility

Implement the Phase 5 HTTP behavior and validation for corrections, filings, state transitions, and timeline/history retrieval. Keep the API behavior aligned with the common contract and document any unresolved contract issue.

### Required work

1. Review the current Phase 4 routes, schemas, error format, authentication middleware, and state-transition logic.
2. Confirm the exact Phase 5 contract before changing route signatures or response fields.
3. Implement the correction operation for authorized users.
   - Validate the incident ID.
   - Validate the replacement decision and required fields.
   - Validate timestamps and evidence references.
   - Preserve the prior decision instead of overwriting history.
   - Return the required conflict or validation errors.
4. Implement the filing operation.
   - Accept the contract’s filing fields.
   - Reject filing when the incident is not eligible.
   - Validate the filing timestamp and required filing metadata.
   - Return the resulting incident state and timeliness classification.
5. Complete the filing-dependent state transitions.
   - MATERIAL_PENDING_FILING should transition correctly after a filing.
   - ON_TIME and LATE behavior must follow the agreed deadline rule.
   - Invalid duplicate or out-of-order filings must produce a defined response.
6. Implement timeline/history retrieval.
   - Include the required incident, evidence, decision, correction, and filing events.
   - Preserve event order and timestamps.
   - Use the exact response shape from the contract.
7. Add API-level tests for every new success and failure behavior before requesting integration.
8. Update API documentation, schemas, and model references when the response shape changes.

### Astha deliverables

- API implementation and schemas
- Unit tests for validation and state transitions
- Route-level tests for corrections, filings, and timeline retrieval
- Updated OpenAPI or contract documentation, if required
- A short handoff note listing routes, request/response examples, known limitations, and dependencies on Srihari’s persistence interfaces

### Astha completion criteria

- New routes return the required status codes and structured errors.
- No invalid request creates or modifies a stored record.
- Correction history remains append-only.
- Filing and timeline responses match the shared contract.
- Existing Phase 3 and Phase 4 routes still pass their tests.
- The branch is ready for Srihari’s persistence integration and Mohit’s acceptance tests.

## Srihari: persistence, calendar, and deployment

### Primary responsibility

Implement the database and deployment support needed by the Phase 5 API. Preserve data across restart, support authorized reset of synthetic data, and ensure deadline/timeliness behavior uses the agreed calendar.

### Required work

1. Review the current PostgreSQL schema, SQLAlchemy models, repository interfaces, migrations, and reset behavior.
2. Add persistence for Phase 5 data as required by the contract.
   - Correction records or replacement-decision records
   - Filing records and filing metadata
   - Timeline/history event data, if not derived safely from existing tables
   - Any required audit or provenance fields
3. Keep the history append-only.
   - Do not delete prior decisions when a correction is recorded.
   - Do not mutate original evidence or filing records.
   - Preserve record ordering and timestamps.
4. Create and test database migrations.
   - Upgrade from the Phase 4 schema.
   - Verify a fresh database migration.
   - Verify downgrade behavior if required by the project workflow.
   - Verify persistence across application restart.
5. Integrate calendar and deadline behavior.
   - Reuse the agreed Eastern Time behavior.
   - Use the approved holiday-list version.
   - Define the due-date boundary and business-day count behavior.
   - Support ON_TIME and LATE classifications consistently.
6. Implement safe reset support for synthetic Phase 5 data.
   - Remove decisions, corrections, filings, and related records created by tests.
   - Verify that reset does not affect unrelated records.
7. Investigate and document any database-clock or timestamp behavior.
8. Deploy the integrated branch only after the local migration and regression checks pass.
9. Record the deployed API URL, tester URL, commit SHA, Cloud Run revision, and deployment timestamp.

### Srihari deliverables

- SQLAlchemy model and repository changes
- Database migration files
- Calendar and filing-timeliness integration
- Restart and reset verification evidence
- Deployment report with API revision and tester revision
- Handoff note documenting persistence interfaces, migration commands, and known limitations

### Srihari completion criteria

- Fresh and upgraded databases both work.
- Decisions, corrections, filings, and timeline data persist correctly.
- Reset behavior is verified with synthetic data.
- Deadline and timeliness calculations match independent expected fixtures.
- The deployed API is reachable and reports the correct commit/revision.
- No secrets are committed or exposed in logs.

## Mohit: testing, CI, integration, and documentation

### Primary responsibility

Design and run independent automated tests for the Phase 5 increment, preserve regression coverage, validate the deployed system, and produce the evidence needed for the phase submission.

### Required work

1. Inspect the final Phase 5 contract and create a requirement-to-test matrix.
2. Add independent fixtures for:
   - Original decisions
   - Corrected decisions
   - Filing before the deadline
   - Filing after the deadline
   - Filing at the exact deadline boundary
   - Invalid and duplicate filings
   - Timeline ordering
   - Reset and restart behavior
3. Add acceptance tests for corrections.
   - Valid correction is recorded.
   - Original decision remains available in history.
   - Invalid correction is rejected.
   - Unknown evidence or incident is rejected.
   - Correction does not create an unauthorized state transition.
4. Add acceptance tests for filings.
   - Filing after a valid material decision succeeds.
   - Filing before, on, and after the deadline is classified correctly.
   - Filing without an eligible decision is rejected.
   - Duplicate or malformed filing is handled according to the contract.
5. Add acceptance tests for timeline/history.
   - Events are complete.
   - Events are in the required order.
   - Timestamps and event types are correct.
   - Corrections do not erase prior history.
6. Add regression tests for Phase 3 and Phase 4 behavior.
7. Add persistence and reset tests.
   - Verify data after restart.
   - Verify reset removes only synthetic test data.
8. Update the tester and CI selection.
   - Add a clear `phase5` marker.
   - Preserve JUnit and JSONL output.
   - Ensure failures propagate to CI.
   - Keep informational checks clearly labeled if they are not merge-blocking.
9. Run local validation and record exact results.
10. Run the deployed suite after Srihari provides the final API revision.
11. Coordinate cross-team testing with the other pod.
   - Agree on a reset window.
   - Run both testing directions.
   - Record timestamps, versions, counts, failures, coverage, and reruns.
12. Update the documentation and prepare the Gradescope evidence package.

### Mohit deliverables

- Phase 5 acceptance tests
- Independent Phase 5 fixtures
- Regression and persistence tests
- CI/tester updates
- Local and deployed test reports
- Cross-team testing report
- Updated models or model-review notes
- Phase 5 completion report with limitations and unresolved issues

### Mohit completion criteria

- Every Phase 5 acceptance criterion has at least one automated test.
- Every new core operation has success, failure, authentication, and boundary coverage.
- Expected values are independent of production calculations.
- Existing Phase 3 and Phase 4 tests pass.
- The final deployed run has saved raw and structured reports.
- Cross-team results are recorded honestly; no missing result is fabricated.
- The final report identifies incomplete functionality, known limitations, and owners.

## Integration order

1. Astha documents the final route and schema contract.
2. Srihari adds persistence, migrations, calendar behavior, and repository interfaces.
3. Astha integrates the route handlers with Srihari’s interfaces.
4. Mohit adds acceptance tests and independent fixtures.
5. All three members review the tests and contract together.
6. Run local migrations, unit tests, acceptance tests, restart checks, reset checks, and static checks.
7. Merge the three branches into `integration`.
8. Run the full integrated suite.
9. Deploy the reviewed integration commit.
10. Run the deployed suite and save the report.
11. Run reciprocal cross-team tests during an exclusive reset window.
12. Update the endpoint registry and project documentation.
13. Submit the Phase 5 artifacts.

## Required evidence before submission

- Deployed API URL
- Deployed tester URL
- API commit SHA and deployment revision
- Tester commit SHA and deployment revision
- Exact test commands
- Local test report
- Deployed test report
- Phase 5 test count and outcome summary
- Regression result for Phase 3 and Phase 4 tests
- Migration and restart evidence
- Reset evidence
- Coverage values, if required by the registry or Gradescope
- Cross-team results for both directions
- Updated model files and locations
- Known limitations and unresolved contract issues
- Endpoint registry update
- Project documentation update

## Suggested repository structure

```text
README-PHASE5.md

docs/
  phase5/
    phase5-plan.md
    phase5-handoff.md
    phase5-test-report.md
    phase5-cross-team-report.md
    phase5-contract-issues.md
  models/
    ECE30861_Phase5_Updated_Models.pdf
  test-results/
    phase5-local.xml
    phase5-deployed.xml

tests/
  acceptance/
    test_phase5_corrections.py
    test_phase5_filings.py
    test_phase5_timeline.py
  fixtures/
    test_phase5_data.py
```

## Branch and commit expectations

Each person should make focused commits and include tests with implementation changes.

Suggested commit prefixes:

- `feat(api): implement Phase 5 correction and filing routes`
- `feat(storage): add Phase 5 persistence and migrations`
- `test(phase5): add correction filing and timeline acceptance tests`
- `ci: enforce Phase 5 test reporting`
- `docs(phase5): update models and delivery report`

Before merging into `main`:

- Confirm the working tree is clean.
- Confirm no secrets are present in the diff.
- Confirm migrations run from a fresh database and an upgraded Phase 4 database.
- Confirm the full suite passes locally.
- Confirm the deployed report matches the deployed commit.
- Confirm all known limitations are documented.
- Confirm the endpoint registry and project documentation are updated.

## Definition of done

Phase 5 is complete only when the system has a coherent new capability, the capability is integrated with the existing service, automated tests cover the new and existing behavior, the reviewed version is deployed, the registry and documentation are updated, and the final report states what remains incomplete and why.
