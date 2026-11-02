# Astha Phase 4 decision API handoff

Owner: Astha. Branch: `phase4/astha-decisions`, based on fetched
`integration` at `e9dd257d6840f41369d6be700dc5d28ec226db42`.

## Scope and implementation status

Schemas, human decision validation, ordinary decision state rules, POST decisions,
GET deadline-status, and incident retrieval integration are implemented and tested
with injected dependencies. **Production Phase 4 is not integrated or complete.**
Srihari's persistent repository and calendar have not been supplied on integration
or another fetched branch. No models, migrations, holiday algorithm, deployment,
CI configuration, tester files, or Mohit acceptance files were changed.

The two new endpoints return 503 `PHASE4_DEPENDENCIES_UNAVAILABLE` until both
adapters are connected. This is an explicit development integration failure,
not a pod-contract success response. With neither adapter configured, Phase 3
continues to use its existing repository. Configuring only one adapter fails
explicitly rather than serving potentially stale incident/decision information.
There is no production in-memory fallback. Test implementations live only in
`tests/unit/decision_fakes.py`.

## Contract review and source limitations

Directly read the local `Phase 2 - Pod.docx` supplied in Astha's Downloads:
REQ-04/05/08/09/10, Q3.3, Q4 AC-06/07/09/10/11/15, Q5.1/Q5.2 and Q6.2/Q6.3.
The embedded image models are not transcribed by XML text extraction; their
state/date rules were cross-checked against Mohit's source review in draft
[PR #13](https://github.com/asthap66/sec-project-ece30861/pull/13), branch
`mohit-phase4` at `1d79f0e9b0b8f063beee0d650b7320ff951ad7b0`.
Read its `readme-phase4.md`, `docs/phase4/contract-review.md`, report, runbook,
45 HTTP tests, and seven independent deadline cases without merging the branch.

The instructor-linked Google document could not be retrieved in this environment.
Mohit's source review identifies the instructor starter OpenAPI as the separate
course tester/system interface, not a domain decision specification. No changes
were made to `/test/*`. Generated `/openapi.json` describes this implementation;
it is not evidence of independent instructor artifact conformance.

Confirmed public bodies:

- POST `/incidents/{incidentId}/decisions`: `decision`, `determinedAt`,
  `decidedBy`, `rationale`, `evidenceIds`. Returns 201 with `decisionId`,
  `status`, `deadline` (date or explicit null).
- GET `/incidents/{incidentId}`: existing fields retained; `currentDecision`
  is null or contains the five request fields plus `decisionId` and `deadline`.
  `filing` remains null; no Phase 5 filing representation is invented.
- GET `/incidents/{incidentId}/deadline-status`: optional RFC 3339 `as_of`;
  returns `status`, `deadline`, `businessDays`. Time defaults to the injected
  server clock. Explicit aware times, including future simulation, are passed
  to the shared calculator without an invented future-time restriction.

Decision strings must be MATERIAL or NOT_MATERIAL. Required text rejects blanks
and preserves submitted text. Evidence references must be a nonempty list of
nonblank strings; every reference must belong to the incident. Timestamps use
the existing RFC 3339 validator and normalize to UTC. Invalid enum responses
match Q5.2's exact `INVALID_DECISION` example. Other errors use existing handlers.

Remaining pod decisions are not resolved by this branch:

- 2025 acceptance dates versus the model's 2026–27 holiday list.
- General businessDays intervals and its integer value when not applicable.
- Equality of discovery/determination: REQ-05/Q5.2 reject **before** discovery,
  so this service allows equality; Model 2's stricter wording needs agreement.
- Duplicate evidence IDs: preserved in order, not silently deduplicated or
  rejected. The adapter must retain the public list if relational links are used.
- Text maxima for new decision fields: none invented.
- Exact codes/messages beyond the supplied enum example.

## Dependency interfaces for Srihari

Typed protocols are in `app/services/decisions.py`. Integration hooks are in
`app/routes/decision_support.py`; all providers are FastAPI dependencies.
Replace the two hook bodies or register application-level overrides with
production provider functions. A storage provider should receive the existing
`Session` through `Depends(get_db)`; do not create a second engine or session.

```python
def provide_decision_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DecisionRepository:
    return YourSQLAlchemyDecisionRepository(session)


app.dependency_overrides[get_decision_repository] = provide_decision_repository
app.dependency_overrides[get_deadline_calculator] = provide_shared_calendar
```

The names beginning `Your`/`provide_shared_calendar` above are explanatory,
not existing production implementations. No guessed imports are installed.

`DecisionRepository.get_incident(id)` returns `IncidentDetail | None`: a detached
snapshot with all incident/evidence fields, latest recorded decision (or null),
and filing-aware state if implemented later. Select current by recording order,
not by submitted determination time. A snapshot decision's deadline may be null;
the feature service computes it through the calendar on every read.

`DecisionRepository.transaction(id)` returns a context manager whose transaction
exposes a fresh `incident` snapshot and `append_decision(DecisionCreate) -> str`.
It must:

1. Lock the incident before loading current decision/evidence and hold through
   commit. Unknown parent raises shared 404 `ApiError`.
2. Serialize conflicting ordinary decisions for that incident. The service
   validates again under this lock; the earlier route existence read is not
   trusted for authorization to write.
3. Append the decision and evidence links, flush to obtain its generated public
   ID, and commit once on successful context exit. Do not commit inside append.
4. Roll back all rows/links on validation, calendar, insert, or commit failure.
5. Coordinate concurrent reset, preserve append-only history, and avoid storing
   a second mutable incident status or calculated deadline.

`DeadlineCalculator.calculate_deadline(aware_datetime) -> date` owns fourth-day
counting, named Eastern timezone conversion, and the versioned shared holiday
list. It is called only for MATERIAL decisions.

`DeadlineCalculator.describe_deadline(date | None, aware_as_of) -> DeadlineStatus`
owns all status/counting arithmetic. Null deadline means NOT_APPLICABLE. Other
results are PENDING/OVERDUE with a date and nonnegative integer businessDays.
Its no-deadline integer convention must be agreed by the pod; zero in the test
stub is only test setup. The service passes explicit as_of or its clock value.

`get_optional_decision_service` composes the adapters once per request. Existing
`get_incident_service` passes that service into `IncidentService`; GET then uses
the decision repository's complete snapshot and derives status/current deadline.
Existing incident creation and evidence insertion still use the shared Phase 3
SQLAlchemy repository. Evidence insertion does not create/change a decision.

## State and validation model

| Current state | Ordinary MATERIAL | Ordinary NOT_MATERIAL |
| --- | --- | --- |
| OPEN | MATERIAL_PENDING_FILING, calculated deadline | NOT_MATERIAL, null deadline |
| NOT_MATERIAL | MATERIAL_PENDING_FILING, new current decision | NOT_MATERIAL, new current decision |
| MATERIAL_PENDING_FILING | 409, unchanged | 409, unchanged |
| FILED | 409, unchanged | 409, unchanged |

Authentication precedes routing. Existing-parent lookup precedes JSON and query
validation, including malformed bodies. Field/time/reference validation precedes
workflow conflicts (Model 4). Routes expose no edits/deletes; unsupported methods
return shared 405 errors. Only explicit human POSTs record decisions. The FILED
guard preserves a future filing-aware adapter's state; no filing endpoint exists.

## Verification

See the final local verification record below. Tests cover schemas, UTC/text
preservation, invalid/mixed references, before/future determination, success,
NOT_MATERIAL-to-MATERIAL, current-decision retrieval, state conflicts, explicit
and default as_of delegation, malformed JSON/query errors, authentication order,
append-only methods, post-decision evidence, missing adapters, calendar failure,
and transaction/commit failures.

The concurrent-call test verifies the service's locked-snapshot contract against
a test lock, not PostgreSQL concurrency. Calendar stubs return fixed results;
these tests do not verify AC-09/10 holiday arithmetic. Real migration, no-orphan
row checks, rollback, concurrency, reset and restart need Srihari's adapter and
disposable PostgreSQL. Mohit's unmerged HTTP suite must be rerun after integration.
No deployed or cross-team Phase 4 success is asserted.

### Mohit fixture issue found during review

At the reviewed PR head, `setup_decision()` calls `create_incident(api)` with
the default `VALID_INCIDENTS[0]`. Its discovery instant is September 21, **2026**.
The default decision and the calendar fixture cases use determination dates in
**2025**. Those intended success cases must return 400 under REQ-05 even after
the missing routes are implemented. Mohit should create those incidents with
an explicitly earlier synthetic discovery instant (for example 2020) while
preserving the independent deadline expectations. His files were not modified.
This is a test-input defect separate from missing production dependencies.

### Final local verification on November 1, 2026

Commands ran in the existing Python 3.12 project virtual environment:

| Check | Result |
| --- | --- |
| `python -m pytest -p no:cacheprovider` | **249 passed, 74 skipped, 0 failed**; 323 collected |
| New decision service/schema/route tests | **62 passed**, included above |
| `python -m ruff check .` | Passed |
| `python -m ruff format --check .` | Passed; 101 files |
| `python -m mypy` | Passed; 67 source files |
| `git diff --check` | Passed |

The 74 skips comprise 48 live acceptance cases without `BASE_URL` and 26
PostgreSQL cases without a disposable `TEST_DATABASE_URL`. Docker and uv were
not available on PATH. No shared/deployed service was used. Mohit's unmerged
Phase 4 suite was reviewed, not copied into this branch or executed against a
stub and reported as end-to-end coverage.

The first run had one existing coverage instrumentation test failure and mypy's
missing `coverage` import. The project environment lacked the already-locked
runtime package. Installing `coverage==7.16.2` resolved both; dependency files
and lockfile were unchanged. One existing Starlette/httpx deprecation warning
remains. Missing Phase 4 adapters are explicitly covered by a passing 503 test;
they remain an integration blocker, not a passing production workflow.
