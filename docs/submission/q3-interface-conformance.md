# Q3 Interface conformance (draft)

Lead: Srihari. Feature details: Astha. Test results: Mohit.

Status of every operation in the pod's common contract (Phase 2 - Pod.pdf,
Q5.1–Q5.3) in the code on the `integration` branch, as of 2026-10-17
(local run: 168 unit/infrastructure tests and 47 acceptance tests passed; against the deployment on 2026-10-18: 48 acceptance tests passed, none skipped). "Yes" means implemented
and covered by a test that passes; the deployed run is recorded in
`docs/test-results/2026-10-18-deployed.md`.

**Update this table as Astha's routes land and as deployed runs are recorded.**
Record real observations only (README §9).

## Operations

| Operation | Contract requirement | Phase | Status | Evidence |
| --- | --- | --- | --- | --- |
| `GET /health` | Public; `200 {status: string}` | 3 | **Yes** | `tests/infrastructure/test_auth.py::test_health_needs_no_key`; AC-14 `test_health_is_public` (local run) |
| `POST /reset` | API key; clears all data; `200 {"status": "RESET_COMPLETE"}` | 3 | **Yes** | `tests/infrastructure/test_database.py::test_reset_clears_everything_and_restarts_ids` |
| `POST /incidents` | Create; `201 {incidentId, status: OPEN}`; 400 naming the bad field | 3 | **Yes** | `tests/acceptance/test_ac01_05_incidents_evidence.py` (AC-01/02), `tests/unit/test_incidents.py`; local run 2026-10-17 |
| `GET /incidents/{incidentId}` | Incident with evidence, `currentDecision`/`filing` null; 404 if unknown | 3 | **Yes** | `test_ac01_05_incidents_evidence.py` (AC-01/03/04) |
| `POST /incidents/{incidentId}/evidence` | `201 {evidenceId, recordedAt}`; 404 for unknown incident | 3 | **Yes** | `test_ac01_05_incidents_evidence.py` (AC-04/05), `tests/unit/test_evidence.py` |
| `POST /incidents/{incidentId}/decisions` | Materiality decision, state rules, deadline | 4 | **No**, planned for Phase 4 | — |
| `POST /incidents/{incidentId}/corrections` | Correct the current decision | 4 | **No**, planned for Phase 4 | — |
| `GET /incidents/{incidentId}/deadline-status` | `NOT_APPLICABLE` / `PENDING` / `OVERDUE`, optional `as_of` | 4 | **No**, planned for Phase 4 | — |
| `POST /incidents/{incidentId}/filing` | Record 8-K filing, `ON_TIME`/`LATE` | 4 | **No**, planned for Phase 4 | — |
| `GET /incidents/{incidentId}/timeline` | Events and evidence counts | 4/5 | **No**, planned | — |
| `POST /test/setup` (course testing interface) | API key; `201 {session_id}`; resets to empty baseline; 409 on reused ID | 3 | **Yes** | `tests/infrastructure/test_test_interface.py`; live tester run 2026-10-18 (`docs/cross-team-testing.md`) |
| `GET /test/report` (course testing interface) | API key; code coverage for the session; 404 unknown | 3 | **Yes** | `tests/infrastructure/test_test_interface.py`; live tester run 2026-10-18 |
| `GET /incidents` (proposed, not in contract) | List incidents (needed by AC-02, AC-16) | — | **Not in contract**; currently returns 405 (only POST exists on `/incidents`). Proposal pending pod agreement | `docs/contract-issues.md` #2 |

## Cross-cutting rules

| Contract rule | Status | Evidence |
| --- | --- | --- |
| `X-API-Key` on every endpoint except `/health`; missing/wrong → 401 (REQ-13) | **Yes** | `test_auth.py`; AC-14 `test_authenticated_route_*` (9 passed locally against Docker) |
| Key checked before routing, body validation or lookup (contract-issues #4, our decision) | **Yes** | `test_auth.py::test_key_is_checked_before_routing` |
| Every error is `{"error": CODE, "message": ...}` (REQ-14) | **Yes** | `test_errors.py::assert_error_format` and the tests that use it |
| Validation failures are 400 naming the field, not 422 (REQ-02, AC-02) | **Yes** | `test_errors.py`; per-route in `tests/unit/test_incidents.py`, `test_evidence.py` and AC-02 acceptance tests. E.g. a future `discoveredAt` → `{"error": "INVALID_DISCOVERED_AT", "message": "discoveredAt: Discovery time must not be in the future"}` |
| Unknown resource → 404 (AC-03) | **Yes** | `test_errors.py`; AC-03 acceptance tests |
| Edit/delete attempts → 405 (REQ-07) | **Yes** | `test_errors.py::test_edit_or_delete_is_405`; `DELETE`/`PUT /incidents/INC-001` → 405 (checked 2026-10-17 against the combined app) |
| Wrong-state operations → 409 (REQ-08) | **No**, Phase 4 (no state-changing operations yet) | — |
| Requests RFC 3339 with offset; responses in UTC (REQ-14) | **Yes** | `discoveredAt: 2026-09-21T14:30:00-04:00` comes back as `2026-09-21T18:30:00Z`; `tests/unit/test_schemas.py`, `test_database.py::test_timestamps_keep_the_instant_and_are_timezone_aware` |
| IDs `INC-001` / `EVD-001` | **Yes** (database-generated) | `test_database.py::test_ids_have_the_contract_format` |
| Data kept across restarts until reset (REQ-15) | **Yes**, deployed | 2026-10-18: 100/100 incidents intact after a Cloud Run restart (new revision), 0 after reset (`scripts/check_persistence.py`) |
| 95% of requests within 1 s at 100 incidents (REQ-15) | **Yes**, deployed | 2026-10-18: 200/200 within 1 s; p50 48 ms, p95 61 ms (`scripts/performance.py`) |
| Deployed over HTTPS (REQ-13) | **Yes** | https://incident-api-356019173418.us-central1.run.app; AC-14 `test_deployment_uses_https` passes; `http://` redirects to `https://` |

## Our choices where the contract is silent

These are applied by our service; they should be confirmed with the other team
so both implementations behave the same (see `docs/contract-issues.md`).

- **Error codes**: `UNAUTHORIZED` (401), `NOT_FOUND` (404),
  `METHOD_NOT_ALLOWED` (405), `INTERNAL_ERROR` (500), and
  `INVALID_<FIELD>` for 400s (e.g. `INVALID_DISCOVERED_AT`), following the
  contract's only example, `INVALID_DECISION`. A malformed JSON body is
  `INVALID_BODY`.
- **Precedence**: the API key is checked before anything else.
- **Field lengths**: `title` ≤ 200 and `description` ≤ 5000 characters, as
  placeholders in `app/config.py` until the pod agrees (contract-issues #3).
- **IDs after reset** restart at `INC-001` / `EVD-001`, so test runs are
  repeatable.
