# readme-phase4

ECE 30861 | SEC Cybersecurity Disclosure Project | Phase 4 execution handbook

Prepared: November 1, 2026

Team: Srihari, Astha, Mohit

Document status: Proposed work assignment and implementation plan, not a completion report.

Repository: https://github.com/asthap66/sec-project-ece30861

## 1. Start here

The Phase 4 deliverable is a working human decision and deadline workflow.
It must be integrated with the existing API, deployed, and independently testable.
Writing submission answers does not substitute for delivering the functionality.
This handbook assigns work; it does not claim that teammates have accepted or completed it.
Confirm assignments together before parallel implementation.

Read Sections 1 through 12 first.
Then read the work packages owned by you.
Use the scenario catalog as a test design reference, not a demand for one test file per scenario.
Parameterize related cases instead of duplicating code.
Only selected, applicable scenarios belong in the release suite.
Exploratory scenarios are explicitly not additional course requirements.

### 1.1 What changes for the user

Before Phase 4, the documented deployment creates incidents and attaches evidence.
After Phase 4, a human reviewer can record a supported materiality decision.
A MATERIAL decision produces the contract-defined incident state and filing deadline.
The user can retrieve the current decision and query deadline status at a supplied time.
Evidence alone must never cause an automatic materiality determination.

The demonstration is:

1. Create an incident with a valid discovery timestamp.
2. Attach evidence to that incident.
3. Submit a human MATERIAL decision referencing that evidence.
4. Observe MATERIAL_PENDING_FILING and the calculated deadline.
5. Retrieve the incident and inspect currentDecision.
6. Request deadline status with a fixed as_of timestamp.
7. Show a pending case and an overdue case.
8. Show one invalid decision rejected without saving anything.
9. Show that Phase 3 behavior still works.

### 1.2 Source grounding and uncertainty

The uploaded Phase 2 - Pod.pdf, Section 6.2, explicitly names this milestone.
It covers REQ-04, REQ-05, REQ-08, REQ-09, and REQ-10.
Its demonstration and validation list AC-06, AC-07, AC-09, and AC-10.
It additionally requires state-conflict and deadline-status tests.
The uploaded Phase 2 Part 2.pdf contains team architecture decisions.
The Phase 4 instructions are in Pasted markdown(20261101-202609).md.
Historical Phase 3 results are available in this conversation and the uploaded Phase 3 report.
The current repository, current branch protections, and current deployment were NOT inspected for this document.
All historical descriptions must be rechecked against the working branch before implementation.
Do not interpret a suggested path as proof that a file already exists.
Do not interpret a proposed function signature as a change to the public API.

### 1.3 Important corrections to earlier planning summaries

AC-09 is standard deadline calculation.
AC-10 is weekend and holiday deadline calculation.
AC-15 is state rules.
AC-11 combines overdue status with on-time and late filing checks.
AC-08 combines correction history with protection against direct edits/deletes.
Do not report all of AC-11 or AC-15 complete when filing-dependent cases are deferred.
Do not report all of AC-08 complete before correction history is implemented.
The original team design proposed derived incident status and on-demand deadline calculation.
Do not silently replace those decisions with separately mutable state and deadline columns.
If the current implementation differs, document the actual design and its consistency guarantees.

## 2. Responsibility split

| Work area | Primary owner | Reviewer / collaborator |
| --- | --- | --- |
| Decision request/response schemas | Astha | Mohit |
| Decision validation and service logic | Astha | Srihari |
| Decision endpoint and incident retrieval | Astha | Mohit |
| Deadline-status endpoint wiring | Astha | Srihari |
| Decision database schema and migration | Srihari | Astha |
| Business-day and holiday calculation module | Srihari | Mohit |
| Database transactions and concurrency support | Srihari | Astha |
| Reset integration | Srihari | Mohit |
| Feature unit tests | Feature author | Other feature author |
| HTTP acceptance tests and fixtures | Mohit | Astha |
| Independent expected calendar results | Mohit | Srihari |
| CI and test isolation | Mohit | Srihari |
| Deployed tester packaging | Srihari | Mohit |
| Cross-team coordination and results | Mohit | Both teammates |
| Deployment and release evidence | Srihari | Mohit |
| State and data diagrams | Astha | Srihari |
| Deadline model | Srihari | Mohit |
| Requirement/test mapping | Mohit | Astha |
| Registry and staff access | Srihari | Mohit |
| Scope and contract agreement | All three | Other team in pod |

### 2.1 Astha's outcome

Deliver the public workflow through the agreed API.
Own the validation and application behavior seen by a caller.
Coordinate the persistence shape with Srihari before writing SQLAlchemy-dependent code.
Use Srihari's calendar module rather than writing a second calendar algorithm in the router.
Write unit/service tests for feature logic; Mohit's HTTP suite is additional evidence.
Update models to reflect the final code instead of the planned code.

### 2.2 Srihari's outcome

Deliver reliable persistence, calendar calculations, and a reproducible deployment.
Implement the database migration and reset ordering.
Make the calendar inputs explicit and versioned with the release.
Coordinate transaction and current-decision semantics with Astha.
Package and deploy the updated tester with Mohit's tests.
Record the application SHA, tester SHA, migration version, and actual release results.

### 2.3 Mohit's outcome

Demonstrate that the new workflow satisfies the agreed contract.
Write assertions for status codes, response data, persistence, and prohibited side effects.
Keep the existing acceptance suite as regression coverage.
Use independent expected dates instead of importing production calculations into assertions.
Coordinate cross-team testing in both directions with agreed reset windows.
Report unknown, skipped, partial, and failed checks accurately.

## 3. Scope and requirement boundaries

| Requirement | Phase 4 treatment | Main evidence |
| --- | --- | --- |
| REQ-04 | Human decisions supported by same-incident evidence | AC-06 and AC-07 |
| REQ-05 | Reject invalid decision times and evidence references | AC-06 plus negative cases |
| REQ-08 | Implement reachable decision-state rules | AC-15 partial where filing is unavailable |
| REQ-09 | Fourth business day after Eastern determination date | AC-09 and AC-10 |
| REQ-10 | NOT_APPLICABLE, PENDING, OVERDUE | Deadline tests and overdue portion of AC-11 |
| REQ-01/03 | Preserve incident and evidence behavior | Existing regression tests |
| REQ-07 | Preserve append-only behavior for new records | Applicable no-edit checks |
| REQ-13/14 | Preserve auth, errors, reset, timestamps | Existing and new route checks |
| REQ-15 | Check persistence and performance after integration | Selected deployed checks |

Corrections, filing recording, timelines, and summaries are Phase 5 in the original milestone sequence.
Do not remove them from the total project scope.
Do not introduce a fake filing implementation just to make a Phase 4 test look complete.
If those operations are already present in the repository, preserve and regression-test them.
If current course instructions expand required scope, reconcile that explicitly before work starts.

## 4. Contract decisions before coding

Read the actual shared contract and instructor-provided OpenAPI artifact.
The rubric links an OpenAPI document; its contents have not been retrieved for this handbook.
Do not claim conformance to that artifact until it has been obtained and compared.
The course testing interface and the domain incident API may have different schemas.
Identify which artifact governs each interface rather than assuming one overrides everything.
Log contradictions with exact fields, examples, owners, and an agreed resolution.

Contract URL from the rubric:
https://docs.google.com/document/d/1GhEVTw3a2tNJY2arfDyWgWS94kVYfgC7/edit

Registry URL from the rubric:
https://docs.google.com/spreadsheets/d/1bTCN3IdCcOPDYIAh7nG7WKNnv9WaAfbdkWfnnK97HL4/edit

Decisions to settle:

- Exact NOT_MATERIAL incident state label from the state model.
- Behavior when another ordinary decision follows NOT_MATERIAL.
- Whether future as_of is allowed for status simulation.
- Meaning of businessDays at, before, and after the due date.
- Whether the status boundary is a date comparison or a specific instant.
- Required fields and null handling for NOT_APPLICABLE.
- Duplicate evidence ID behavior.
- Required error codes and message constraints.
- Error precedence when authentication, resource lookup, and body validation all fail.
- Authoritative holiday dates, observed holidays, and supported years.
- Remaining provisional text-length limits.
- Whether AC-02 no-write evidence can use database checks or needs shared interface support.

Use the source contract where it already answers these questions.
Do not turn every item into a new negotiation if the answer is already explicit.
Any shared-scope reduction requires the approvals described by the assignment.

## 5. Confirmed domain behavior from Phase 2

A decision records MATERIAL or NOT_MATERIAL.
The request includes determinedAt, decidedBy, rationale, and evidenceIds.
At least one referenced evidence item must belong to that incident.
A determination before discovery is rejected.
A determination in the future is rejected.
An evidence ID belonging to another incident is rejected.
REQ-05 specifies 400 and no saved decision for those invalid cases.
REQ-08 specifies 409 and no state change for a new ordinary decision while MATERIAL_PENDING_FILING.
The software must not choose or recommend materiality on its own.
Request timestamps include an RFC 3339 offset.
Timestamp responses are normalized to UTC.
Date responses use YYYY-MM-DD.

### 5.1 Domain decision example from the Phase 2 contract

```json
{
  "decision": "MATERIAL",
  "determinedAt": "2026-09-22T15:00:00-04:00",
  "decidedBy": "Disclosure Committee",
  "rationale": "The operational and financial impact was determined to be material.",
  "evidenceIds": ["EVD-001"]
}
```

The example success response is HTTP 201:

```json
{
  "decisionId": "DEC-001",
  "status": "MATERIAL_PENDING_FILING",
  "deadline": "2026-09-28"
}
```

These are reference examples, not permission to hardcode IDs or timestamps.
Tests must obtain generated incident/evidence IDs from actual setup responses.
Cross-check examples with the final agreed artifact before using them as fixtures.

### 5.2 Deadline reference cases copied from acceptance criteria

| Criterion | Determination date | Expected deadline |
| --- | --- | --- |
| AC-09 | 2025-09-29 | 2025-10-03 |
| AC-10 | 2025-10-10 | 2025-10-17 |
| AC-10 | 2025-11-25 | 2025-12-02 |
| AC-10 | 2025-12-30 | 2026-01-06 |
| AC-10 | 2025-10-04 | 2025-10-09 |

Count the fourth business day AFTER the determination's Eastern calendar date.
The determination date itself is not day one.
Skip weekends and holidays in the pod's agreed list.
These dates specify project behavior; this handbook is not an independent legal interpretation.
For AC-11's overdue-only case, no filing with deadline 2025-10-03 is OVERDUE as of 2025-10-06.
Do not infer all boundary businessDays values from this single example.

## 6. Architecture and module boundaries

The team design proposed append-only decision rows and derived incident state.
The team design proposed a pure calendar function and on-demand deadline calculation.
Inspect the current implementation before deciding whether to retain or explicitly revise those choices.
One component must own the meaning of current decision.
One component must own the calculation of incident status.
One calendar module must own date calculation for all relevant endpoints.
One agreed holiday fixture must feed the implementation and be identified in reports.
Expected answers in tests must not be computed by calling that production module.

Suggested internal interfaces, subject to repository conventions:

```python
def calculate_deadline(determined_at, holiday_dates):
    """Return the contract deadline date from an aware timestamp."""


def describe_deadline(current_decision, as_of, holiday_dates):
    """Return domain status and business-day information."""


def record_decision(session, incident_id, payload, now):
    """Validate and persist one decision atomically."""
```

These signatures are design sketches, not executable implementation instructions.
Use existing types and dependency injection patterns when available.
Pass an explicit current time into domain validation to make time-sensitive tests deterministic.
Do not add an unauthenticated production clock-control endpoint for tests.
Use timezone-aware values and a named Eastern timezone, not a permanent UTC-04 offset.
Keep the decision and incident-state changes atomic if status is stored.
If status is derived, test that all read endpoints derive it consistently.
Use locking or a database-enforced invariant to prevent conflicting concurrent decisions.
Choose the exact invariant after confirming whether later decisions from NOT_MATERIAL are allowed.

## 7. Suggested repository locations

All new paths below are proposals; adapt them to the existing structure.
Do not create duplicate frameworks or move unrelated files to match this example.

```text
app/
  routes/                 decision and deadline-status route additions
  services/               decision validation and workflow logic
  domain/                 pure calendar and status logic, if this layer exists
  models/                 decision persistence, if models are split into a package
tests/
  unit/                   isolated calendar and validation cases
  integration/            real PostgreSQL transaction and migration cases
  acceptance/             public HTTP contract scenarios
  fixtures/               agreed synthetic inputs and independent expected outputs
docs/
  phase4/                 scope, decisions, ownership, handoffs
  models/                 updated diagrams and source
  test-results/           timestamped deployed and cross-team results
```

Locate the real migration directory and modify it in place.
Locate the real tester entrypoint before changing discovery or packaging.
Locate the real CI workflow before adding commands or job dependencies.

## 8. Execution order and handoffs

Gate A: Inventory current code and compare contract artifacts.
Gate B: Freeze payloads, model shape, calendar semantics, and function interfaces.
Gate C: Build persistence, calendar logic, API behavior, and tests in parallel.
Gate D: Integrate all changes and pass local/CI regression checks.
Gate E: Deploy the reviewed application and tester revisions.
Gate F: Run own-service and cross-team suites against identified versions.
Gate G: Correct mismatches, rerun affected coverage, update evidence and models.

Astha can start schema and validation tests after Gate B.
Srihari can start migration and pure calendar work after Gate B.
Mohit can write contract fixtures and acceptance tests after Gate B.
Tests can initially fail because the features are absent; record that as development state.
Do not merge a misleading green suite that skips every new feature without disclosure.
Only use the actual final deployed run for release claims.

## 9. Branch and merge conventions

The historical working branch was integration; confirm the current release branch.
Suggested feature branches are phase4/astha-decisions, phase4/srihari-calendar-storage, and phase4/mohit-tests.
These are suggestions, not claims that branches have been created.
Keep migrations under one primary owner to avoid conflicting migration heads.
Keep public schema changes under one primary owner to avoid incompatible payloads.
Review shared files together before merging simultaneous edits.
Do not overwrite another teammate's uncommitted work.
Do not force-push a shared branch to simplify integration.
Keep each pull request focused on one coherent change and its verification.
Record dependency PRs when a feature depends on a migration or calculator interface.
Verify branch protection actually exists before saying CI blocks merges.

## 10. Testing priorities

Release priority: the named acceptance criteria, public success/failure paths, and Phase 3 regression behavior.
Release priority: decision persistence, no-write rejection, correct currentDecision, and contract calendar fixtures.
Release priority: both directions of cross-team testing and deployed evidence.
Risk priority: concurrency, rollback, time boundaries, and deterministic test setup.
Exploratory priority: larger stress matrices and optional hardening beyond the milestone.
The catalog below provides candidate cases; avoid duplicating equivalent checks across every layer.
Use unit tests for many calendar combinations and HTTP tests for representative integrated cases.
Use database tests for transactional invariants that the public API cannot observe directly.
Use source review for the no-automatic-materiality part of AC-07.
Use infrastructure inspection for claims that HTTP alone cannot establish.

## 11. Definition of done

- [ ] Scope matches Phase 2 Section 6.2 or a recorded approved change.
- [ ] Contract artifacts were compared and discrepancies recorded.
- [ ] New database migration applies to an existing Phase 3 database.
- [ ] Decision creation, retrieval integration, and deadline status work through HTTP.
- [ ] Invalid requests produce agreed errors without unintended writes.
- [ ] Human decision responsibility is preserved.
- [ ] Exact AC-09 and AC-10 reference dates pass.
- [ ] Applicable state-conflict cases pass; deferred filing cases are disclosed.
- [ ] Existing incident/evidence/auth/reset tests still pass.
- [ ] CI and static checks run on the release commit.
- [ ] Application and tester are deployed with identifiable versions.
- [ ] Full own-service suite has a saved final report.
- [ ] Full cross-team runs occur in both directions with saved reports.
- [ ] Coverage dimensions are defined and missing figures are labelled unavailable.
- [ ] Models and documentation match delivered behavior.
- [ ] Registry and staff-access instructions are current.
- [ ] Test duration is measured rather than copied from another team.
- [ ] Remaining defects have an owner and next step.

## 12. Read the work packages correctly

Every package starts as NOT STARTED; this is a planning artifact.
The owner implements or coordinates it, while the reviewer checks evidence.
Work package IDs are local planning IDs and are not official REQ/AC identifiers.
Suggested tests are verification activities, not statements that tests already exist.
Use NOT APPLICABLE with a reason for checks outside the delivered scope.
Use BLOCKED with the exact dependency instead of pretending agreement exists.
The checklist is deliberately detailed so coding agents receive bounded tasks.
The human owner remains responsible for reviewing generated behavior.
## 13. Detailed work packages
### W001: Inventory the actual starting point

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: All Phase 4 work.
Dependency: Repository access.

Implementation steps:
1. Record active branch and SHA.
2. List implemented routes and their tests.
3. Compare repository behavior with the Phase 3 report.
4. Record already-completed work so nobody rebuilds it.

Required handoff: Inventory naming real files, routes, commits, and gaps.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W002: Reconcile domain API artifacts

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04/05/08/09/10.
Dependency: Source artifacts available.

Implementation steps:
1. Read pod Section 5 and state model.
2. Obtain the instructor-linked artifact.
3. Compare fields, enums, response shapes, and errors.
4. Record discrepancies with exact source locations.

Required handoff: Contract comparison with unresolved items and owners.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W003: Confirm milestone and acceptance mapping

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Phase 2 Section 6.2.
Dependency: Source artifacts available.

Implementation steps:
1. Map REQ-04/05/08/09/10 to planned changes.
2. Map AC-06/07/09/10 to tests.
3. Identify partial AC-11 and AC-15 coverage.
4. Separate future filing and correction obligations.

Required handoff: Requirement matrix that does not overclaim complete criteria.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W004: Freeze holiday inputs

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-09.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Locate the shared holiday list.
2. Confirm observed dates and supported years.
3. Version the file with the code.
4. Record how missing or invalid calendar data is handled.

Required handoff: Identified calendar version plus exact reference-date results.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W005: Confirm state transitions

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-08.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Read the actual state model.
2. Confirm NOT_MATERIAL state and later-decision behavior.
3. Specify duplicate ordinary decision rejection.
4. Record unreachable filing-related transitions as deferred.

Required handoff: Reviewed transition table with allowed actions and errors.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W006: Resolve deadline-status semantics

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-10.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Enumerate as_of cases from contract.
2. Confirm boundary and businessDays meanings.
3. Compare NOT_APPLICABLE response fields.
4. Record pod agreement for unresolved behavior.

Required handoff: Independent expected-status fixtures with rationale.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W007: Resolve earlier validation ambiguities

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-02 and AC-02.
Dependency: Both teams reachable.

Implementation steps:
1. Check whether field limits were already agreed.
2. Compare implementation limits between teams.
3. Agree a no-write verification method.
4. Avoid adding list/count endpoints without agreement.

Required handoff: Decision log for limits and AC-02 evidence.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W008: Agree persistence interfaces

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Decision storage.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Review current models with Astha.
2. Choose relationship and current-decision representation.
3. Specify repository/service inputs.
4. Identify shared files and migration ownership.

Required handoff: Short persistence interface handoff.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W009: Create decision migration

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04 persistence.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Add decision fields using project conventions.
2. Add incident/evidence relationships.
3. Preserve existing rows on upgrade.
4. Review constraints against legitimate later history.

Required handoff: Migration applied to a seeded Phase 3 database.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W010: Implement decision ORM mapping

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04 persistence.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Map IDs and timestamps.
2. Represent referenced evidence relationships.
3. Avoid cross-incident links.
4. Keep later corrections possible without overwriting history.

Required handoff: Model tests with real PostgreSQL.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W011: Define transaction ownership

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04/05/08.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Identify where commit occurs.
2. Validate before persisting.
3. Keep decision and stored state atomic.
4. Rollback rejected and failed operations.

Required handoff: Transaction test proving no partial decision state.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W012: Prevent concurrent conflicting decisions

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Risk.
Status: NOT STARTED in this planning document.
Scope: REQ-08.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Identify allowed sequential behavior.
2. Choose lock or constraint strategy.
3. Exercise two competing valid submissions.
4. Verify resulting state is reachable and consistent.

Required handoff: Concurrency test with documented expected outcome.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W013: Extend reset to decisions

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-14.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Inventory dependent tables.
2. Delete or truncate in safe order.
3. Reset identifiers only as specified.
4. Retain API-key protection and repeatability.

Required handoff: Reset succeeds after decision data exists.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W014: Implement Eastern date conversion

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-09.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Require aware input.
2. Convert using named Eastern timezone.
3. Extract calendar date after conversion.
4. Avoid a fixed year-round offset.

Required handoff: Tests for equivalent instants and midnight crossings.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W015: Implement business-day predicate

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-09.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Reject weekends as business days.
2. Consult the agreed holiday set.
3. Keep inputs explicit.
4. Handle the supported year range consistently.

Required handoff: Unit checks for weekday, weekend, and agreed holiday.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W016: Implement fourth-business-day counting

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-09.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Start counting after determination date.
2. Advance calendar dates.
3. Increment only on business days.
4. Return a date without incidental time fields.

Required handoff: All five AC-09/10 examples match exactly.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W017: Implement deadline status calculation

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-10.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Accept explicit as_of.
2. Handle absence of material decision.
3. Apply agreed due-date boundary.
4. Calculate businessDays using defined semantics.

Required handoff: Fixed-clock pending and overdue tests.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W018: Validate calendar configuration

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Risk.
Status: NOT STARTED in this planning document.
Scope: REQ-09 reliability.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Load the agreed file predictably.
2. Detect malformed entries.
3. Avoid silently using a different holiday calendar.
4. Expose actionable startup or validation errors.

Required handoff: Negative configuration test and documented failure mode.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W019: Implement decision request schema

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04/05.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Use contract field names.
2. Validate required text and decision enum.
3. Require aware determinedAt.
4. Validate evidenceIds structure.

Required handoff: Schema tests for each rejected field class.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W020: Implement decision response schema

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Use contract success status.
2. Return generated decisionId.
3. Return contract state and deadline fields.
4. Avoid exposing ORM/internal fields.

Required handoff: Exact response-shape assertions.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W021: Validate evidence ownership

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-05.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Resolve all evidence references.
2. Check each belongs to incident.
3. Reject any invalid reference atomically.
4. Avoid accepting a valid subset of mixed evidence.

Required handoff: Cross-incident and mixed-list tests leave no decision.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W022: Validate determination times

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-05.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Compare instants rather than timestamp strings.
2. Reject before discovery.
3. Reject after injected current time.
4. Confirm equality boundaries from contract.

Required handoff: Fixed-clock boundary tests.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W023: Enforce ordinary decision state rules

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-08.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Read current state consistently.
2. Allow agreed initial decision.
3. Reject disallowed subsequent ordinary decision.
4. Preserve state and currentDecision on rejection.

Required handoff: 409 response plus unchanged-state assertion.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W024: Implement decision service

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04/05/08.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Compose schema and domain validation.
2. Call calendar module for material decisions.
3. Persist in one transaction.
4. Return a domain result independent of HTTP serialization.

Required handoff: Service success and rollback tests.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W025: Wire POST decisions route

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: POST /incidents/{incidentId}/decisions.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Reuse authentication and session dependencies.
2. Call decision service.
3. Map expected errors to contract responses.
4. Preserve request ID and commit headers.

Required handoff: HTTP success, 400, 401, 404, and applicable 409 cases.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W026: Update incident retrieval

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: GET /incidents/{incidentId}.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Load current decision.
2. Serialize supported decision details.
3. Keep incident/evidence fields compatible.
4. Avoid fabricating filing data.

Required handoff: Round-trip test after recording decision.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W027: Wire deadline-status route

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: GET /incidents/{incidentId}/deadline-status.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Parse optional as_of.
2. Reuse ownership/auth conventions.
3. Call pure status logic.
4. Serialize agreed null and businessDays fields.

Required handoff: HTTP pending, overdue, not-applicable, and error cases.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W028: Preserve no automatic materiality

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: AC-07.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Review evidence ingestion.
2. Review status derivation.
3. Ensure severe evidence leaves OPEN without decision.
4. Remove any inferred materiality suggestion from workflow.

Required handoff: Behavior test and source-review note.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W029: Preserve append-only API behavior

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-07.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Check unsupported edit/delete methods.
2. Ensure new routes do not expose generic mutation.
3. Keep accepted decision records immutable.
4. Use only agreed reset for test cleanup.

Required handoff: Method checks and unchanged decision data.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W030: Maintain standardized errors

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-14.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Use existing exception handlers.
2. Confirm missing-field behavior.
3. Avoid raw database exceptions.
4. Keep domain and course-testing error formats distinct.

Required handoff: Response schema checks for new failure paths.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W031: Preserve evidence after decision

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-03 regression.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Read the contract rule allowing evidence additions.
2. Avoid accidentally freezing evidence when status changes.
3. Ensure new evidence does not create a new decision.
4. Preserve existing evidence IDs.

Required handoff: Post-decision evidence regression test.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W032: Create independent calendar oracle fixtures

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: AC-09/10.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Copy exact source dates.
2. Document business-day counting for each.
3. Have another teammate review expected dates.
4. Keep expected values outside production calculation code.

Required handoff: Reviewed fixture file with source references.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W033: Create decision acceptance fixtures

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: AC-06.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Build incidents and evidence through API.
2. Use IDs returned by setup.
3. Keep dates valid relative to discovery.
4. Create malformed variants without changing unrelated fields.

Required handoff: Reusable fixtures and minimal negative inputs.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W034: Test material decision round trip

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Submit valid MATERIAL.
2. Check 201 and response fields.
3. Retrieve currentDecision.
4. Check exact deadline and state.

Required handoff: Automated HTTP acceptance scenario.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W035: Test not-material behavior

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-04/10.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Submit valid NOT_MATERIAL.
2. Check agreed incident state.
3. Check deadline absence.
4. Verify subsequent evidence alone changes no decision.

Required handoff: Automated HTTP test using confirmed enum/shape.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W036: Test negative decision input

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-05.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Exercise missing and malformed fields.
2. Exercise before-discovery and future timestamps.
3. Exercise foreign evidence.
4. Assert errors and no new decision.

Required handoff: Parameterized tests mapped to validation requirements.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W037: Test state conflicts

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-08.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Create a material pending incident.
2. Submit a second ordinary decision.
3. Expect 409.
4. Retrieve and compare original decision and state.

Required handoff: Conflict regression with no-write check.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W038: Test deterministic deadline queries

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-10.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Use supplied as_of.
2. Assert pending and overdue values.
3. Check no-decision response.
4. Keep wall-clock defaults in separate tests.

Required handoff: Reproducible status tests on both deployments.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W039: Test authentication on new routes

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-13.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Use missing key.
2. Use invalid key.
3. Use valid key.
4. Ensure failures reveal no protected decision data.

Required handoff: New-route authentication matrix.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W040: Extend reset acceptance tests

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-14.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Create incident/evidence/decision.
2. Reset only during allowed window.
3. Verify known IDs are absent.
4. Repeat reset and verify valid new setup.

Required handoff: Cleanup and repeatability evidence.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W041: Preserve Phase 3 regressions

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Existing delivered functionality.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Run previous acceptance selection.
2. Investigate changes in response shape.
3. Retain HTTPS handling appropriate to target.
4. Explain intentional updates with contract evidence.

Required handoff: Old-suite report on integrated Phase 4 code.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W042: Add database no-write tests

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-05.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Use isolated PostgreSQL.
2. Capture relevant rows before request.
3. Issue invalid decision.
4. Compare rows and relationships afterward.

Required handoff: Database-backed test rather than status-only assertion.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W043: Make CI environments independent

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Risk.
Status: NOT STARTED in this planning document.
Scope: Test isolation.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Inspect current service-container setup.
2. Use separate database state per run.
3. Avoid parallel tests sharing destructive reset.
4. Clean up only owned test resources.

Required handoff: Two CI runs do not interfere.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W044: Update CI test discovery

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Regression and new feature tests.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Include new test directories.
2. Keep locked dependency installation.
3. Apply migrations before database tests.
4. Ensure failures propagate as failed jobs.

Required handoff: CI run showing actual new tests executed.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W045: Verify static-check scope

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Code quality.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Run Ruff lint.
2. Run format check.
3. Run configured mypy checks.
4. Record commands and actual results.

Required handoff: Recent CI links and output.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W046: Check merge and release controls

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Risk.
Status: NOT STARTED in this planning document.
Scope: Process improvement.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Inspect actual branch rules.
2. Coordinate required checks with maintainers.
3. Avoid locking out legitimate collaborators.
4. Record enforced versus manual controls accurately.

Required handoff: Configuration evidence or explicit documented limitation.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W047: Map tests to requirements

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Traceability.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Assign official REQ/AC references.
2. Distinguish exercised from fully satisfied.
3. Separate inspection evidence.
4. Record deferred filing/correction portions.

Required handoff: Updated test mapping with honest status.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W048: Package updated tester

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Course testing interface.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Locate actual tester entrypoint.
2. Include new tests and fixtures.
3. Preserve required setup/run/report contract.
4. Verify target base URL and credentials are configurable.

Required handoff: Tester can execute the expanded suite.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W049: Check report accounting

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Coverage and run totals.
Dependency: Gate B: agreed contract and interfaces.

Implementation steps:
1. Count pass/fail/error/skip separately.
2. Define each coverage denominator.
3. Avoid counting missing endpoint as implemented.
4. Mark unavailable measurements explicitly.

Required handoff: Report matches raw test results.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W050: Deploy schema and application

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Release.
Dependency: Gate D: integrated checks pass.

Implementation steps:
1. Record target release SHA.
2. Apply migration using established process.
3. Deploy image matching SHA.
4. Verify readiness before cross-team runs.

Required handoff: Deployment identifiers and health evidence.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W051: Deploy tester version

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Release.
Dependency: Integrated tester checks pass.

Implementation steps:
1. Build reviewed tester code.
2. Record its version independently.
3. Verify fixtures are packaged.
4. Check run/report readiness without triggering shared resets.

Required handoff: Tester version and safe smoke-check evidence.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W052: Run full suite on own deployment

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q4.5 evidence.
Dependency: Gate E: reviewed deployment.

Implementation steps:
1. Confirm deployed commit.
2. Reserve reset window.
3. Run full applicable suite.
4. Save raw results and explain failures/skips.

Required handoff: Timestamped own-service report.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W053: Run suite on other team

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q6.1 evidence.
Dependency: Other team ready and reset window agreed.

Implementation steps:
1. Exchange current URLs and credentials privately.
2. Agree test window and supported contract.
3. Run full suite against their base URL.
4. Share reproducible mismatches and coverage.

Required handoff: Our-tests-to-their-service report.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W054: Obtain reverse cross-team run

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q6.1 evidence.
Dependency: Other team tester available.

Implementation steps:
1. Provide own deployed version and access instructions.
2. Ask other team for their full run.
3. Collect raw counts and coverage definitions.
4. Classify failures jointly without assuming ownership.

Required handoff: Their-tests-to-our-service report.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W055: Verify persistence across restart

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-15 regression.
Dependency: Exclusive validation window.

Implementation steps:
1. Create representative incidents/evidence/decisions.
2. Record known IDs and values.
3. Restart application without destroying database.
4. Verify stored decisions and derived state survive.

Required handoff: Before/after evidence tied to same image.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W056: Check deployed performance

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: REQ-15 regression.
Dependency: Stable deployed version.

Implementation steps:
1. Use agreed workload.
2. Record sample count and latency distribution.
3. Identify version and environment.
4. Avoid generalizing one run into a service guarantee.

Required handoff: Measured latency report with workload definition.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W057: Update state and data models

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q5 artifacts.
Dependency: Integrated implementation available.

Implementation steps:
1. Reflect actual decision relationships.
2. Show implemented transitions.
3. Label future correction/filing features as planned.
4. Review model against code with Srihari.

Required handoff: Diagram source and rendered diagrams.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W058: Update deadline model

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q5 artifacts.
Dependency: Integrated calculator available.

Implementation steps:
1. Show Eastern date conversion.
2. Show weekend/holiday filtering.
3. Show counting and status evaluation.
4. Separate specified rules from unresolved assumptions.

Required handoff: Model matching calendar module and fixtures.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W059: Update test and limitation documentation

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q7 artifacts.
Dependency: Final test reports available.

Implementation steps:
1. Record implemented scope.
2. List remaining failures and partial criteria.
3. Assign defect owners and target phases.
4. Preserve reproducible evidence links.

Required handoff: Current docs reflecting deployed state.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W060: Update registry and staff instructions

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q2.2 operational work.
Dependency: Final deployments available.

Implementation steps:
1. Confirm system and tester base URLs.
2. Describe authentication for each.
3. Provide measured or clearly estimated runtime.
4. Confirm staff credential delivery privately.

Required handoff: Registry row and credential handoff confirmation.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W061: Record run duration

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Registry runtime.
Dependency: A completed test run.

Implementation steps:
1. Measure wall-clock duration of actual tester run.
2. Record target and suite size.
3. Distinguish observation from maximum timeout.
4. Add a sensible labelled operational allowance.

Required handoff: Measured duration and configured timeout if one exists.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W062: Record implementation AI verification

Owner: Astha.
Reviewer: Mohit; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q8 supporting evidence.
Dependency: During development.

Implementation steps:
1. Keep bounded task descriptions.
2. Review generated behavior against contract.
3. Record a genuine correction when one occurs.
4. Do not invent an anecdote for the submission.

Required handoff: Short factual implementation log.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W063: Record infrastructure AI verification

Owner: Srihari.
Reviewer: Astha; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q8 supporting evidence.
Dependency: During development.

Implementation steps:
1. Record generated migration/deployment tasks.
2. Inspect resulting scripts.
3. Verify secrets handling and deployment outcome.
4. Save real corrections and reviewer decisions.

Required handoff: Short factual infrastructure log.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W064: Record test AI verification

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Q8 supporting evidence.
Dependency: During development.

Implementation steps:
1. Record generated fixture/test tasks.
2. Review assertions independently.
3. Check a focused deliberate fault if useful.
4. Record actual weak assertions corrected.

Required handoff: Short factual testing log.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
### W065: Close release evidence packet

Owner: Mohit.
Reviewer: Srihari; involve the named collaborator from the ownership table when needed.
Priority: Release.
Status: NOT STARTED in this planning document.
Scope: Submission preparation.
Dependency: Gate F/G complete.

Implementation steps:
1. Collect exact application and tester versions.
2. Link CI and both-direction reports.
3. Reconcile models and operation status.
4. Mark unresolved blockers plainly.

Required handoff: One reviewed evidence index.

Completion checks:
- [ ] The owner identifies the actual files or external artifact changed.
- [ ] The reviewer can reproduce or inspect the claimed result.
- [ ] Relevant contract assumptions are confirmed or explicitly unresolved.
- [ ] Any skipped verification has a concrete reason.
- [ ] The result names the code version when behavior depends on code.

Stop condition: a required contract decision is ambiguous or dependencies are absent.
On that condition, record BLOCKED with the exact missing input and responsible person.
Do not mark this package complete solely because an agent reports success.
## 14. Scenario catalog
Each scenario below is a candidate verification case, not an assertion that it already passes.
Release cases support the milestone; Conditional cases require contract applicability first.
Risk cases are selected by remaining risk; Deferred cases must not be counted as delivered.
HTTP setup must use public endpoints and returned identifiers unless explicitly stated otherwise.
Database-only evidence does not prove that another team can observe the same property through HTTP.
Combine equivalent cases with parameterization and avoid redundant execution solely to increase counts.
### T001: Standard Monday Unit

Area: Calendar reference.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-09-29; for HTTP create earlier discovery and same-incident evidence.

Act:
- Calculate deadline using agreed calendar.

Assert:
- Deadline equals 2025-10-03 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T002: Standard Monday HTTP

Area: Calendar reference.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-09-29; for HTTP create earlier discovery and same-incident evidence.

Act:
- Record MATERIAL and retrieve deadline.

Assert:
- Deadline equals 2025-10-03 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T003: Columbus Day interval Unit

Area: Calendar reference.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-10-10; for HTTP create earlier discovery and same-incident evidence.

Act:
- Calculate deadline using agreed calendar.

Assert:
- Deadline equals 2025-10-17 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T004: Columbus Day interval HTTP

Area: Calendar reference.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-10-10; for HTTP create earlier discovery and same-incident evidence.

Act:
- Record MATERIAL and retrieve deadline.

Assert:
- Deadline equals 2025-10-17 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T005: Thanksgiving interval Unit

Area: Calendar reference.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-11-25; for HTTP create earlier discovery and same-incident evidence.

Act:
- Calculate deadline using agreed calendar.

Assert:
- Deadline equals 2025-12-02 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T006: Thanksgiving interval HTTP

Area: Calendar reference.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-11-25; for HTTP create earlier discovery and same-incident evidence.

Act:
- Record MATERIAL and retrieve deadline.

Assert:
- Deadline equals 2025-12-02 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T007: New Year interval Unit

Area: Calendar reference.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-12-30; for HTTP create earlier discovery and same-incident evidence.

Act:
- Calculate deadline using agreed calendar.

Assert:
- Deadline equals 2026-01-06 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T008: New Year interval HTTP

Area: Calendar reference.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-12-30; for HTTP create earlier discovery and same-incident evidence.

Act:
- Record MATERIAL and retrieve deadline.

Assert:
- Deadline equals 2026-01-06 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T009: Saturday determination Unit

Area: Calendar reference.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-10-04; for HTTP create earlier discovery and same-incident evidence.

Act:
- Calculate deadline using agreed calendar.

Assert:
- Deadline equals 2025-10-09 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T010: Saturday determination HTTP

Area: Calendar reference.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use determination date 2025-10-04; for HTTP create earlier discovery and same-incident evidence.

Act:
- Record MATERIAL and retrieve deadline.

Assert:
- Deadline equals 2025-10-09 exactly.

Oracle basis: AC-09/AC-10 explicitly name this date.
### T011: decision: missing

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only decision to the missing case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T012: decision: null

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only decision to the null case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T013: decision: wrong JSON type

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only decision to the wrong JSON type case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T014: determinedAt: missing

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only determinedAt to the missing case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T015: determinedAt: null

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only determinedAt to the null case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T016: determinedAt: wrong JSON type

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only determinedAt to the wrong JSON type case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T017: decidedBy: missing

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only decidedBy to the missing case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T018: decidedBy: null

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only decidedBy to the null case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T019: decidedBy: wrong JSON type

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only decidedBy to the wrong JSON type case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T020: rationale: missing

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only rationale to the missing case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T021: rationale: null

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only rationale to the null case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T022: rationale: wrong JSON type

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only rationale to the wrong JSON type case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T023: evidenceIds: missing

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only evidenceIds to the missing case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T024: evidenceIds: null

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only evidenceIds to the null case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T025: evidenceIds: wrong JSON type

Area: Decision schema.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Start from an otherwise valid decision payload.

Act:
- Change only evidenceIds to the wrong JSON type case.

Assert:
- Reject according to agreed schema; verify contract error and unchanged currentDecision.

Oracle basis: A single-field mutation isolates validation responsibility.
### T026: decidedBy: empty string

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit decidedBy with empty string.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T027: decidedBy: whitespace-only string

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit decidedBy with whitespace-only string.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T028: decidedBy: non-ASCII text

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit decidedBy with non-ASCII text.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T029: decidedBy: at agreed maximum

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit decidedBy with at agreed maximum.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T030: decidedBy: one beyond agreed maximum

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit decidedBy with one beyond agreed maximum.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T031: rationale: empty string

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit rationale with empty string.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T032: rationale: whitespace-only string

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit rationale with whitespace-only string.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T033: rationale: non-ASCII text

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit rationale with non-ASCII text.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T034: rationale: at agreed maximum

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit rationale with at agreed maximum.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T035: rationale: one beyond agreed maximum

Area: Decision text.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use a valid incident with evidence and record relevant agreed text constraint.

Act:
- Submit rationale with one beyond agreed maximum.

Assert:
- Apply the agreed field rule; successful accepted content must round-trip; rejected content must not save.

Oracle basis: Length and whitespace semantics must be sourced rather than invented.
### T036: unknown enum

Area: Decision enum.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Valid decision fixture.

Act:
- Replace decision with unknown enum.

Assert:
- Reject unless the agreed schema explicitly permits normalization; never infer a decision.

Oracle basis: Materiality values must follow the shared contract.
### T037: lowercase material

Area: Decision enum.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Valid decision fixture.

Act:
- Replace decision with lowercase material.

Assert:
- Reject unless the agreed schema explicitly permits normalization; never infer a decision.

Oracle basis: Materiality values must follow the shared contract.
### T038: number instead of enum

Area: Decision enum.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Valid decision fixture.

Act:
- Replace decision with number instead of enum.

Assert:
- Reject unless the agreed schema explicitly permits normalization; never infer a decision.

Oracle basis: Materiality values must follow the shared contract.
### T039: boolean instead of enum

Area: Decision enum.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Valid decision fixture.

Act:
- Replace decision with boolean instead of enum.

Assert:
- Reject unless the agreed schema explicitly permits normalization; never infer a decision.

Oracle basis: Materiality values must follow the shared contract.
### T040: One evidence ID

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Reference one existing item belonging to the incident.

Assert:
- Accept a valid human decision.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T041: Multiple evidence IDs

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Reference multiple items belonging to the incident.

Assert:
- Accept and preserve agreed evidence association semantics.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T042: Empty evidence list

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Send evidenceIds as an empty list.

Assert:
- Reject; no decision is saved.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T043: Unknown evidence ID

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Reference an ID absent from the database.

Assert:
- Reject according to contract; no decision is saved.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T044: Foreign evidence ID

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Reference evidence from another incident.

Assert:
- Return contract rejection, including 400 for REQ-05 ownership violation.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T045: Mixed valid and foreign IDs

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Reference one owned and one foreign evidence item.

Assert:
- Reject the entire decision; do not save the valid subset.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T046: Mixed valid and unknown IDs

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Reference one owned and one nonexistent evidence item.

Assert:
- Reject the entire decision.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T047: Repeated evidence ID

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Repeat one owned evidence ID in the list.

Assert:
- Follow recorded pod decision on duplicates; never silently assume semantics.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T048: Evidence object instead of ID

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Place an object inside evidenceIds.

Assert:
- Reject structure/type error according to schema.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T049: Null evidence element

Area: Evidence association.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Create two incidents with distinct evidence and retain returned IDs.

Act:
- Place null inside evidenceIds.

Assert:
- Reject invalid element according to schema.

Oracle basis: REQ-04/05 require traceable same-incident support.
### T050: before discovery

Area: Decision time.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt before discovery.

Assert:
- 400 and no write.

Oracle basis: REQ-05 and timestamp formatting rules.
### T051: equal to discovery

Area: Decision time.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt equal to discovery.

Assert:
- Apply explicit boundary interpretation; REQ-05 only forbids before discovery.

Oracle basis: REQ-05 and timestamp formatting rules.
### T052: after discovery but before now

Area: Decision time.
Primary owner: Mohit.
Verification layer: Unit/integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt after discovery but before now.

Assert:
- Accept when other fields are valid.

Oracle basis: REQ-05 and timestamp formatting rules.
### T053: equal to injected now

Area: Decision time.
Primary owner: Mohit.
Verification layer: Unit/integration.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt equal to injected now.

Assert:
- Use agreed precision and boundary; do not rely on network timing.

Oracle basis: REQ-05 and timestamp formatting rules.
### T054: after injected now

Area: Decision time.
Primary owner: Mohit.
Verification layer: Unit/integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt after injected now.

Assert:
- 400 and no write.

Oracle basis: REQ-05 and timestamp formatting rules.
### T055: missing timezone offset

Area: Decision time.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt missing timezone offset.

Assert:
- Reject invalid timestamp.

Oracle basis: REQ-05 and timestamp formatting rules.
### T056: malformed timestamp

Area: Decision time.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt malformed timestamp.

Assert:
- Reject invalid timestamp.

Oracle basis: REQ-05 and timestamp formatting rules.
### T057: equivalent offset representation

Area: Decision time.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use fixed discovery and injected current time for unit/integration checks.

Act:
- Submit determinedAt equivalent offset representation.

Assert:
- Compare instants correctly, not timestamp strings.

Oracle basis: REQ-05 and timestamp formatting rules.
### T058: Initial MATERIAL

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- OPEN incident and valid evidence.

Act:
- Record MATERIAL.

Assert:
- 201; MATERIAL_PENDING_FILING; expected deadline.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T059: Initial NOT_MATERIAL

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- OPEN incident and valid evidence.

Act:
- Record NOT_MATERIAL.

Assert:
- 201; state from agreed model; no applicable material deadline.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T060: Ordinary decision while pending

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Incident with current MATERIAL decision.

Act:
- Submit another ordinary decision.

Assert:
- 409; original decision and state unchanged.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T061: Evidence alone

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- OPEN incident with severe descriptive evidence.

Act:
- Retrieve incident and deadline status.

Assert:
- OPEN and NOT_APPLICABLE; no generated materiality decision.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T062: Evidence after material decision

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- MATERIAL_PENDING_FILING incident.

Act:
- Attach another valid evidence item.

Assert:
- Evidence addition succeeds under Phase 2 rule; current decision remains unchanged.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T063: Decision after NOT_MATERIAL

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Incident with NOT_MATERIAL decision.

Act:
- Submit another ordinary decision.

Assert:
- Follow actual state model; stop if unspecified.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T064: Decision after filing

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Deferred.
Execution status: NOT RUN.

Arrange:
- FILED incident only if filing exists.

Act:
- Submit a decision.

Assert:
- 409 with no change; otherwise mark unavailable in Phase 4.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T065: Correction after filing

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Deferred.
Execution status: NOT RUN.

Arrange:
- FILED incident only if corrections and filing exist.

Act:
- Submit a correction.

Assert:
- 409 with no change; otherwise defer.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T066: Filing while OPEN

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Deferred.
Execution status: NOT RUN.

Arrange:
- OPEN incident only if filing operation exists.

Act:
- Submit filing.

Assert:
- 409 with no change; otherwise defer.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T067: Two concurrent MATERIAL requests

Area: Workflow.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Isolated OPEN incident with valid evidence.

Act:
- Issue two simultaneous valid decisions.

Assert:
- Result must match allowed serialized workflow; no incompatible current decisions.

Oracle basis: REQ-04/08; filing-dependent portions of AC-15 are not automatically delivered.
### T068: No decision

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- OPEN incident.

Act:
- GET deadline-status with fixed as_of.

Assert:
- NOT_APPLICABLE with agreed response fields.

Oracle basis: REQ-10 and explicit shared status semantics.
### T069: Not material

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- NOT_MATERIAL current decision.

Act:
- GET deadline-status.

Assert:
- NOT_APPLICABLE with agreed response fields.

Oracle basis: REQ-10 and explicit shared status semantics.
### T070: Before due date

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Material incident with fixed deadline.

Act:
- Query earlier as_of.

Assert:
- PENDING with independently counted businessDays.

Oracle basis: REQ-10 and explicit shared status semantics.
### T071: At due date

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Material incident with fixed deadline.

Act:
- Query on due date.

Assert:
- Apply explicit agreed boundary and businessDays convention.

Oracle basis: REQ-10 and explicit shared status semantics.
### T072: After due date

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Deadline 2025-10-03 and no filing.

Act:
- Query as_of on 2025-10-06.

Assert:
- OVERDUE; derive count from agreed definition.

Oracle basis: REQ-10 and explicit shared status semantics.
### T073: Weekend after due date

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Friday deadline with no filing.

Act:
- Query Saturday and Sunday.

Assert:
- Use agreed overdue boundary; count business days separately from elapsed calendar days.

Oracle basis: REQ-10 and explicit shared status semantics.
### T074: Holiday after due date

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Known holiday after deadline.

Act:
- Query within holiday.

Assert:
- Use agreed day-count and status boundary.

Oracle basis: REQ-10 and explicit shared status semantics.
### T075: Missing as_of

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Material incident away from a boundary.

Act:
- Query without as_of.

Assert:
- Uses server clock according to contract.

Oracle basis: REQ-10 and explicit shared status semantics.
### T076: Malformed as_of

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Valid incident.

Act:
- Query as_of=not-a-timestamp.

Assert:
- Contract validation error; not 500.

Oracle basis: REQ-10 and explicit shared status semantics.
### T077: Offset-free as_of

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Valid incident.

Act:
- Query timestamp without offset.

Assert:
- Apply agreed timestamp rule.

Oracle basis: REQ-10 and explicit shared status semantics.
### T078: Future as_of

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Valid material incident.

Act:
- Query a future as_of.

Assert:
- Follow agreed simulation behavior; do not confuse with future determinedAt rejection.

Oracle basis: REQ-10 and explicit shared status semantics.
### T079: Repeated query

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Unchanged material incident.

Act:
- Repeat identical explicit as_of.

Assert:
- Identical contract result.

Oracle basis: REQ-10 and explicit shared status semantics.
### T080: Read-only query

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Capture incident and decision data.

Act:
- Query several as_of values.

Assert:
- No mutation of persisted decisions or state.

Oracle basis: REQ-10 and explicit shared status semantics.
### T081: Equivalent as_of instants

Area: Deadline status.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Choose one instant in two timezone representations.

Act:
- Query both representations.

Assert:
- Same status and businessDays.

Oracle basis: REQ-10 and explicit shared status semantics.
### T082: UTC midnight crossing

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Use a UTC timestamp whose Eastern date is previous day.

Assert:
- Count from Eastern date, not UTC date.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T083: Summer offset

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Use a summer determination.

Assert:
- Named timezone applies daylight-time conversion.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T084: Winter offset

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Use a winter determination.

Assert:
- Named timezone applies standard-time conversion.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T085: Spring transition

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Use aware instants around spring transition.

Assert:
- Convert valid instants consistently without assuming every day has 24 hours.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T086: Fall transition

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Use distinct aware instants around repeated local hour.

Assert:
- Preserve instant meaning and correct Eastern date.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T087: Month boundary

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Determine near end of a month.

Assert:
- Continue business-day count into next month.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T088: Year boundary

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Determine near end of a year.

Assert:
- Load holidays for every year crossed.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T089: Leap-year February

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Choose supported leap-year inputs.

Assert:
- Advance dates correctly through February 29.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T090: Observed holiday

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Choose an observed date on agreed calendar.

Assert:
- Skip precisely the agreed observed date.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T091: Missing year coverage

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Choose a year outside supported calendar data.

Assert:
- Explicit documented behavior; no silent inaccurate deadline.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T092: Duplicate holiday entries

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Load repeated dates.

Assert:
- No double subtraction or altered count.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T093: Weekend holiday entry

Area: Calendar boundaries.
Primary owner: Srihari.
Verification layer: Unit.
Priority: Risk.
Execution status: NOT RUN.

Arrange:
- Use supported, independently reviewed fixture dates and fixed times.

Act:
- Include holiday that is also weekend.

Assert:
- Skip day once; do not extend deadline twice.

Oracle basis: Timezone and calendar assumptions are high-risk correctness boundaries.
### T094: POST decisions with missing key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call POST decisions with missing key.

Assert:
- 401 without protected data or writes.

Oracle basis: New routes must inherit existing authentication.
### T095: POST decisions with wrong key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call POST decisions with wrong key.

Assert:
- 401 without protected data or writes.

Oracle basis: New routes must inherit existing authentication.
### T096: POST decisions with valid key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call POST decisions with valid key.

Assert:
- Normal contract behavior; auth does not reject valid access.

Oracle basis: New routes must inherit existing authentication.
### T097: GET deadline-status with missing key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call GET deadline-status with missing key.

Assert:
- 401 without protected data or writes.

Oracle basis: New routes must inherit existing authentication.
### T098: GET deadline-status with wrong key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call GET deadline-status with wrong key.

Assert:
- 401 without protected data or writes.

Oracle basis: New routes must inherit existing authentication.
### T099: GET deadline-status with valid key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call GET deadline-status with valid key.

Assert:
- Normal contract behavior; auth does not reject valid access.

Oracle basis: New routes must inherit existing authentication.
### T100: GET incident after decision with missing key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call GET incident after decision with missing key.

Assert:
- 401 without protected data or writes.

Oracle basis: New routes must inherit existing authentication.
### T101: GET incident after decision with wrong key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call GET incident after decision with wrong key.

Assert:
- 401 without protected data or writes.

Oracle basis: New routes must inherit existing authentication.
### T102: GET incident after decision with valid key

Area: Authentication.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use an existing incident; for POST prepare otherwise valid decision.

Act:
- Call GET incident after decision with valid key.

Assert:
- Normal contract behavior; auth does not reject valid access.

Oracle basis: New routes must inherit existing authentication.
### T103: PUT incident

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt PUT against incident.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T104: PUT evidence

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt PUT against evidence.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T105: PUT decision

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt PUT against decision.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T106: PATCH incident

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt PATCH against incident.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T107: PATCH evidence

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt PATCH against evidence.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T108: PATCH decision

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt PATCH against decision.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T109: DELETE incident

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt DELETE against incident.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T110: DELETE evidence

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt DELETE against evidence.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T111: DELETE decision

Area: Append-only behavior.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Identify an actual contract-defined resource path; do not invent a detail endpoint.

Act:
- Attempt DELETE against decision.

Assert:
- Contract 405 where that path/method rule applies; stored values unchanged.

Oracle basis: REQ-07; distinguish unsupported methods from nonexistent paths.
### T112: Decision survives restart

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Restart app with persistent DB retained.

Assert:
- Same decision ID, fields, evidence links, and current status.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T113: Invalid decision no row

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Submit invalid decision and inspect DB.

Assert:
- No decision or relationship rows added.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T114: Rejected conflict no overwrite

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Submit second ordinary decision while pending.

Assert:
- Original row values and current pointer unchanged.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T115: Failure midway through write

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Inject controlled persistence failure in isolated test.

Assert:
- Transaction rollback leaves consistent original state.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T116: Migration preserves incidents

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Upgrade seeded Phase 3 schema.

Assert:
- Existing incidents and evidence remain retrievable.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T117: Fresh schema creation

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Apply migrations to empty disposable DB.

Assert:
- All required tables and constraints exist.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T118: Repeated app startup

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Start app again against already migrated DB.

Assert:
- No duplicate schema or destructive data initialization.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T119: Reset after decisions

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Reset an isolated fixture database.

Assert:
- Decision relationships and parent data cleared safely.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T120: Repeated reset

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Reset twice in reserved window.

Assert:
- Both calls follow reset contract without foreign-key failure.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T121: Reset auth rejection

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Request reset with invalid key.

Assert:
- No database rows removed.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T122: New records after reset

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Create incident, evidence, and decision after reset.

Assert:
- Valid relationships and agreed identifier behavior.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T123: Evidence linked to several decisions

Area: Persistence.
Primary owner: Srihari.
Verification layer: Integration.
Priority: Conditional.
Execution status: NOT RUN.

Arrange:
- Use isolated PostgreSQL or an explicitly reserved deployed test window.

Act:
- Use legitimate history only if supported.

Assert:
- Constraints permit intended append-only history; no accidental uniqueness restriction.

Oracle basis: Persistence and atomicity require evidence beyond HTTP status.
### T124: Create incident regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Run existing create/retrieve test.

Assert:
- Input fields still round-trip.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T125: Attach evidence regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Run existing category and association tests.

Assert:
- Evidence is stored and returned unchanged.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T126: Invalid incident regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Run existing malformed-input cases.

Assert:
- Existing error behavior remains compatible.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T127: Health regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Call public health without key.

Assert:
- Expected public response.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T128: Unknown incident regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Request unknown incident and child operation.

Assert:
- Contract resource-not-found behavior.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T129: Request logging regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Inspect representative request logs.

Assert:
- Method, path, status, timing, and correlation remain available.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T130: Commit identity regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Inspect response header.

Assert:
- Matches deployed application version.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T131: HTTPS regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Call deployed HTTPS endpoint.

Assert:
- Transport and application response succeed.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T132: Existing no-edit regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Run old forbidden mutation cases.

Assert:
- No accidental CRUD exposure.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T133: Existing fixtures regression

Area: Phase 3 regression.
Primary owner: Mohit.
Verification layer: HTTP.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use existing tests and setup conventions; preserve test meaning.

Act:
- Run existing fixture consumers.

Assert:
- New schema does not silently invalidate unrelated fixture expectations.

Oracle basis: Phase 4 must remain compatible with delivered Phase 3 functionality.
### T134: Tester packages new fixtures

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Run packaged tester against known test service.

Assert:
- Calendar and decision fixtures load successfully.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T135: Tester target override

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Point configuration at second team.

Assert:
- Requests target configured URL without source edits.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T136: Tester key separation

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Use tester auth separately from target API auth if required.

Assert:
- Credentials reach the correct service only.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T137: Tester failure propagation

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Use controlled failing target locally.

Assert:
- Run report records failure rather than returning false success.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T138: Tester skip accounting

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Run with one explicitly unavailable scenario.

Assert:
- Skip is counted with reason; not converted to pass.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T139: Coverage denominator

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Inspect generated report.

Assert:
- Denominators and unavailable metrics are explicit.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T140: Run version metadata

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Complete a full run.

Assert:
- Target SHA and tester SHA are distinguishable.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T141: Runtime measurement

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Time actual full suite.

Assert:
- Recorded duration includes stated setup/run scope.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T142: Cross-team safe GET

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Inspect outgoing GET requests.

Assert:
- No unnecessary JSON request body sent.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
### T143: Secrets in output

Area: Tester and reports.
Primary owner: Mohit.
Verification layer: Tester integration.
Priority: Release.
Execution status: NOT RUN.

Arrange:
- Use actual testing-interface contract and isolated fixtures.

Act:
- Review captured reports and logs.

Assert:
- No API keys or database credentials included.

Oracle basis: Course-staff execution and accurate reporting are release deliverables.
## 15. Integration handoff templates

### 15.1 Astha to Srihari

```text
PR/branch:
Base SHA:
Decision payload contract version:
Required database fields and relationships:
Current-decision lookup semantics:
Transaction boundary:
Calculator inputs and expected outputs:
Validation errors requiring domain support:
Unit/service tests completed:
Known blockers:
```

### 15.2 Srihari to Astha

```text
PR/branch:
Migration revision:
How to apply locally:
Actual ORM/repository interfaces:
Calendar module signature:
Holiday data location and version:
Status derivation decision:
Concurrency strategy:
Reset changes:
Verification evidence:
```

### 15.3 Mohit to feature owners

```text
Scenario ID and official REQ/AC:
Contract version:
Target commit:
Minimal setup:
Request without credentials:
Expected response and source:
Actual response:
State before and after:
Reproduction command or test name:
Suspected classification: system / test / specification / environment
Owner and next action:
```

### 15.4 Release handoff

```text
Application SHA:
Tester SHA:
Migration version:
Holiday fixture version:
System base URL:
Tester base URL:
Required auth header names, without values:
CI run:
Own-service report:
Cross-team outgoing report:
Cross-team incoming report:
Observed runtime:
Known skips and failures:
Reset window/contact:
```

## 16. Cross-team execution runbook

### Before the run

- [ ] Confirm both teams are using the agreed interface version.
- [ ] Exchange current base URLs rather than relying on old chat messages.
- [ ] Identify tester authentication separately from target-service authentication.
- [ ] Exchange secrets privately using the team's approved method.
- [ ] Reserve a window for reset and setup operations.
- [ ] Record the target version and tester version.
- [ ] Confirm whether the course setup endpoint itself clears data.
- [ ] Confirm no persistence/performance run is currently sharing the target.
- [ ] Use a dedicated synthetic dataset.
- [ ] Confirm planned timeout and where run reports are collected.

### During the run

- [ ] Start one suite at a time against shared destructive state.
- [ ] Capture the actual start and completion timestamps with timezone.
- [ ] Retain raw test counts, including errors and skips.
- [ ] Keep request/response evidence free of credentials.
- [ ] Investigate failures before attributing them to the other team.
- [ ] Check for HTML/proxy responses that never reached the application.
- [ ] Check version drift if behavior changes mid-run.
- [ ] Check logs for unexpected reset calls before diagnosing data loss.
- [ ] Stop destructive retries if another team reports active interference.
- [ ] Record whether the report is final, interrupted, or superseded.

### After the run

- [ ] Report test totals and supported coverage dimensions.
- [ ] State which criteria are partial rather than fully verified.
- [ ] Attach minimal reproducible failures.
- [ ] Assign system, test, specification, or environment ownership.
- [ ] Agree the fix and rerun plan.
- [ ] If code changes, identify the new version before rerunning.
- [ ] Keep the failed report as history and label the final replacement report.
- [ ] Release the reset window explicitly.
- [ ] Update the evidence index.
- [ ] Request the reverse-direction report if not yet received.

## 17. Deployment runbook

The historical host was Cloud Run with Cloud SQL PostgreSQL.
The historical application runtime was Python/FastAPI/Uvicorn.
These are baseline facts to verify, not a requirement to migrate infrastructure.
Use the current established deployment script after inspecting it.

### Pre-release

- [ ] Select the reviewed commit rather than deploying an untracked worktree.
- [ ] Verify database migration compatibility with retained Phase 3 data.
- [ ] Review dependency and runtime changes.
- [ ] Confirm holiday configuration ships in the image or approved configuration.
- [ ] Confirm database and API credentials are configured without printing values.
- [ ] Confirm target database is the intended deployment database.
- [ ] Record the prior revision for application rollback.
- [ ] Decide migration recovery separately from application rollback.
- [ ] Do not assume rolling back an image reverses a database migration.
- [ ] Coordinate downtime or destructive validation windows with podmates.

### Post-release

- [ ] Verify health and public documentation routes.
- [ ] Verify missing-key requests are rejected.
- [ ] Verify a valid authenticated read.
- [ ] Verify the deployed commit identifier.
- [ ] Run a complete representative decision workflow.
- [ ] Check exact known deadline fixture output.
- [ ] Inspect logs for application errors and migration failures.
- [ ] Confirm tester can target the released application.
- [ ] Run the full applicable suite and save its report.
- [ ] Confirm the service remains available after validation.

## 18. Observability checklist

Log request IDs so failures can be connected across test output and server logs.
Log method, path, status, and duration using existing middleware.
Log safe resource identifiers when useful.
For calendar debugging, log the Eastern date and computed deadline when appropriate.
Do not log API-key values, database URLs, or full sensitive incident payloads.
Distinguish validation failures from unexpected exceptions.
Keep log timestamps explicit about timezone.
Save one small real deployed excerpt for evidence.
Do not fabricate example log lines and label them as observed.
Treat metrics from a local test server separately from deployed-service metrics.

## 19. Coverage and reporting rules

Code coverage describes executed source locations under a particular instrumentation setup.
It does not prove assertions are adequate.
Component coverage requires a defined component inventory and counting rule.
System/model coverage requires defined criteria or transitions and their exercise rules.
Unavailable measurement is not zero and is not full coverage.
Partial AC coverage is not complete AC satisfaction.
A failing call reaching a router must not automatically count as successful operation conformance.
Keep pass, fail, error, and skip totals separate.
Do not compare coverage fractions from different instrumentation as if they were identical measures.
Do not reuse Phase 3 counts as Phase 4 results.
Do not reuse the historical f551649 SHA as the new release SHA without checking the actual release.
Keep examples and measured outcomes visibly separate.

## 20. Definition of useful failure evidence

A useful failure report contains the exact operation and a minimal input.
It identifies the source requirement or agreed fixture.
It identifies the target application version.
It identifies the test-suite version.
It records expected and actual output without secrets.
It records whether state changed unexpectedly.
It states whether the failure is reproducible in isolation.
It records whether an overlapping reset or deployment occurred.
It names the owner and next action.
It avoids claiming a system bug when only the client is known to fail.

## 21. Model updates

Astha owns the delivered incident state diagram.
Include the actual NOT_MATERIAL state label from the agreed model.
Include implemented decision transitions and their conditions.
Show correction and filing transitions separately as planned if they remain absent.
Do not draw unimplemented components as delivered components.

Astha and Srihari jointly review the data model.
Show Incident, Evidence, Decision, and real relationships.
Show the actual representation of evidence references.
Show current-decision semantics without inventing a second source of truth.
Label cardinality and important constraints.

Srihari owns the deadline behavior model.
Show aware timestamp conversion to Eastern date.
Show counting after the determination date.
Show shared calendar filtering.
Show status evaluation with explicit as_of.

Mohit verifies each model against representative tests.
Record at least one actual model/code divergence and its resolution if one occurs.
Do not invent a divergence solely to fill a response field.
If the requested example is unclear, review the original Phase 2 models against the final code.

## 22. Repository documentation updates

- [ ] README describes the new end-to-end workflow.
- [ ] API operation status lists all contract operations, including deferred ones.
- [ ] Setup instructions include new migrations and calendar data.
- [ ] Test instructions identify target URL and auth configuration.
- [ ] Cross-team instructions explain destructive setup/reset behavior.
- [ ] Known limitations describe actual remaining defects.
- [ ] Contract log records genuine agreements with dates and participants.
- [ ] Diagrams have editable source and a readable rendered form.
- [ ] Test reports identify final application and tester versions.
- [ ] Registry runtime is measured or clearly labelled as an estimate.
- [ ] Staff access has been confirmed separately from private peer access.
- [ ] Secrets are absent from repository documentation.

## 23. Instructions for coding agents

Give an agent the actual repository instructions and relevant contract sections.
Assign one work package or a coherent related group.
Specify the files it may need to coordinate with teammates.
Require it to inspect existing patterns before adding parallel abstractions.
Require source-backed field names and response shapes.
Require it to mark unresolved contract questions rather than inventing semantics.
Require tests that verify externally meaningful behavior.
Require it to distinguish executed checks from suggested checks.
Require a changed-file summary, verification results, and remaining limitations.
Do not allow an agent to report deployment success from a local test result.
Do not allow generated expected outputs to simply call production logic.
Do not let generated summaries inflate partial acceptance criteria into full coverage.

### 23.1 Astha agent task outline

```text
Inspect repository instructions, the current implementation, and the agreed Phase 4 contract.
Implement the decision workflow and route integration assigned to Astha in readme-phase4.md.
Coordinate database and calculator interfaces with Srihari's actual work.
Preserve Phase 3 behavior and existing authentication/error conventions.
Write feature tests; do not assume Mohit's acceptance suite replaces unit/service verification.
Stop only the ambiguous portion when a contract rule is missing; document the exact question.
Report actual changes, executed checks, and unresolved dependencies honestly.
```

### 23.2 Srihari agent task outline

```text
Inspect existing models, migrations, calendar conventions, and deployment tooling.
Implement the assigned persistence and pure calendar components.
Use the agreed holiday fixture and independent reference cases.
Preserve existing data during schema upgrade and keep reset dependencies correct.
Coordinate public response integration with Astha and tester packaging with Mohit.
Do not execute shared destructive operations without an agreed window.
Report migration/version evidence and actual executed verification.
```

### 23.3 Mohit agent task outline

```text
Inspect existing acceptance tests, fixture conventions, CI, and tester discovery.
Implement contract-based decision, deadline, state-conflict, and regression tests.
Keep expected dates independent of production calendar code.
Use API-returned IDs and deterministic timestamps; preserve meaningful failure assertions.
Separate local database verification from public black-box checks.
Do not mark unavailable features as passing or silently skip all new tests.
Produce actual test mappings and reports without fabricating cross-team execution.
```

## 24. Historical lessons to preserve

Phase 3 had a persistence attempt disrupted by overlapping reset calls.
The corrective action was an isolated rerun; the preventive lesson is test isolation.
The other team's initial GET requests contained unnecessary JSON bodies.
The corrected run removed those client-side failures.
The remaining AC-02 count assertion was limited by the absence of a public list/count operation.
Coverage reporting differed between the two services.
CI results were reviewed manually because enforced blocking was not confirmed.
Treat these as historical lessons and recheck current status before claiming they are still defects.

## 25. Assignment wording caveats

The Phase 4 rubric contains some Phase 3 wording and references to earlier milestone sections.
Do not assume that copied wording authorizes skipping the next increment.
Use the explicit Phase 4 assignment goal and Phase 2 Section 6.2 for this implementation plan.
Ask course staff if an inconsistency materially changes required scope or reporting.
The rubric states that cross-team results affect grading starting in Phase 4.
It requires deployed validation, relevant updated models, and current project documentation.
It does not require a new frontend for the API-based increment described here.
It does not say that code-quality cleanup alone replaces new user-visible capability.

## 26. Final team review agenda

1. Astha demonstrates the human decision workflow through the public API.
2. Srihari explains persistence and the agreed calendar calculation.
3. Mohit demonstrates an invalid request and its no-write verification.
4. The team checks one exact AC-09 case and one holiday case.
5. The team checks pending and overdue status with explicit as_of.
6. The team checks historical Phase 3 behavior still works.
7. The team compares actual deployment versions with the evidence reports.
8. The team reviews incoming and outgoing cross-team findings.
9. The team marks partial criteria and remaining Phase 5 obligations.
10. Each teammate reviews their own AI-use notes and implementation explanation.

## 27. Reference inventory

Primary supplied source: Phase 2 - Pod.pdf, especially Sections 3, 4, 5, and 6.2.
Primary supplied source: Phase 2 Part 2.pdf, especially Sections 7.2 through 7.4.
Primary supplied source: Pasted markdown(20261101-202609).md, Phase 4 rubric.
Historical source: ECE 30861 - Phase 3.pdf and submitted-results discussion.
Pending comparison source: instructor-linked OpenAPI document listed above.
Current implementation source: repository and final deployed revisions, to be inspected by the team.

This document creates a work plan only.
No production code, branch protection, deployment, registry row, or external message was changed by creating it.
All unchecked items remain pending until the team records real evidence.


## Mohit implementation handoff — November 1, 2026

Mohit-owned independent work is implemented on `mohit-phase4`: HTTP milestone
selection, manual calendar fixtures, regression-preserving CI selection, tester
summary counts, and test/integration instructions. See
[the detailed report](docs/phase4/mohit-phase4-report.md) for executed results,
contract dependencies, and remaining release checks. This does not mark Astha's
or Srihari's features complete, or claim deployed/cross-team Phase 4 success.


Mohit source-review follow-up: the supplied v1.0 PDFs now confirm the decision
schema, NOT_MATERIAL state and subsequent MATERIAL transition, and Eastern
deadline date boundary. The HTTP suite has 45 Phase 4 cases. See
[contract review](docs/phase4/contract-review.md) for remaining ambiguities and
[the report](docs/phase4/mohit-phase4-report.md) for final baseline results.
