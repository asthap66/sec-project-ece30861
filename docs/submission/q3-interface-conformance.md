# Q3 Interface conformance (draft)

Lead: Srihari. Feature details: Astha. Test results: Mohit.

Status of every operation in the pod's common contract (Phase 2 - Pod.pdf,
Q5.1–Q5.3) in the code on the `integration` branch. "Yes" means implemented
and covered by a test that passes; it is not a claim about the deployed service
until the deployed run is recorded in `docs/test-results/`.

**Update this table as Astha's routes land and as deployed runs are recorded.**
Record real observations only (README §9).

## Operations

| Operation | Contract requirement | Phase | Status | Evidence |
| --- | --- | --- | --- | --- |
| `GET /health` | Public; `200 {status: string}` | 3 | **Yes** | `tests/infrastructure/test_auth.py::test_health_needs_no_key`; AC-14 `test_health_is_public` (local run) |
| `POST /reset` | API key; clears all data; `200 {"status": "RESET_COMPLETE"}` | 3 | **Yes** | `tests/infrastructure/test_database.py::test_reset_clears_everything_and_restarts_ids` |
| `POST /incidents` | Create; `201 {incidentId, status: OPEN}`; 400 naming the bad field | 3 | **No** (Astha, in progress) | — |
| `GET /incidents/{incidentId}` | Incident with evidence, `currentDecision`/`filing` null; 404 if unknown | 3 | **No** (Astha, in progress) | — |
| `POST /incidents/{incidentId}/evidence` | `201 {evidenceId, recordedAt}`; 404 for unknown incident | 3 | **No** (Astha, in progress) | — |
| `POST /incidents/{incidentId}/decisions` | Materiality decision, state rules, deadline | 4 | **No**, planned for Phase 4 | — |
| `POST /incidents/{incidentId}/corrections` | Correct the current decision | 4 | **No**, planned for Phase 4 | — |
| `GET /incidents/{incidentId}/deadline-status` | `NOT_APPLICABLE` / `PENDING` / `OVERDUE`, optional `as_of` | 4 | **No**, planned for Phase 4 | — |
| `POST /incidents/{incidentId}/filing` | Record 8-K filing, `ON_TIME`/`LATE` | 4 | **No**, planned for Phase 4 | — |
| `GET /incidents/{incidentId}/timeline` | Events and evidence counts | 4/5 | **No**, planned | — |
| `GET /incidents` (proposed, not in contract) | List incidents (needed by AC-02, AC-16) | — | **Not in contract**; proposal pending pod agreement | `docs/contract-issues.md` #2 |

## Cross-cutting rules

| Contract rule | Status | Evidence |
| --- | --- | --- |
| `X-API-Key` on every endpoint except `/health`; missing/wrong → 401 (REQ-13) | **Yes** | `test_auth.py`; AC-14 `test_authenticated_route_*` (9 passed locally against Docker) |
| Key checked before routing, body validation or lookup (contract-issues #4, our decision) | **Yes** | `test_auth.py::test_key_is_checked_before_routing` |
| Every error is `{"error": CODE, "message": ...}` (REQ-14) | **Yes** | `test_errors.py::assert_error_format` and the tests that use it |
| Validation failures are 400 naming the field, not 422 (REQ-02, AC-02) | **Yes**, framework-level | `test_errors.py::test_missing_field_is_400_naming_it`; per-route coverage comes with Astha's routes |
| Unknown resource → 404 (AC-03) | **Yes**, framework-level | `test_errors.py::test_unknown_path_is_404_in_contract_format` |
| Edit/delete attempts → 405 (REQ-07) | **Partial** | `test_errors.py::test_edit_or_delete_is_405` passes for existing paths (`/reset`). `DELETE /incidents/INC-001` returns 404 until the incident route exists; once `GET /incidents/{incidentId}` is in, other methods on it return 405 automatically (to re-check then) |
| Wrong-state operations → 409 (REQ-08) | **No**, Phase 4 (no state-changing operations yet) | — |
| Requests RFC 3339 with offset; responses in UTC (REQ-14) | **Partial**: stored as timezone-aware instants; request parsing and UTC responses are in Astha's schemas | `test_database.py::test_timestamps_keep_the_instant_and_are_timezone_aware` |
| IDs `INC-001` / `EVD-001` | **Yes** (database-generated) | `test_database.py::test_ids_have_the_contract_format` |
| Data kept across restarts until reset (REQ-15) | **Yes** locally | Restart check, 2026-10-16: `INC-001` present after `docker compose restart app`, gone after reset. Deployed check pending |
| 95% of requests within 1 s at 100 incidents (REQ-15) | **Not measured** | Mohit's performance script (needs the create route) |
| Deployed over HTTPS (REQ-13) | **No**: not deployed yet | AC-14 `test_deployment_uses_https` skips for local targets |

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
