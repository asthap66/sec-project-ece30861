# Requirement / test traceability

Owner: Mohit. Feeds submission Q4.

This table covers local, CI and deployed runs, and each run is recorded in this folder. "Final" means the deployed commit `f551649`. "Earlier" means `ed5f449` (acceptance) or `f2b607c` (AC-16).

| Criterion | Tests | Status |
| --- | --- | --- |
| AC-01 (REQ-01, REQ-14) | `test_ac01_create_then_retrieve_returns_identical_values[4]`, `test_ac01_each_incident_gets_a_distinct_id` | Pass: CI, earlier, and final (via tester) |
| AC-02 (REQ-02, REQ-14) | `test_ac02_invalid_incident_is_rejected_naming_the_field[10]` (black box: 400 naming the field) | Pass: CI, earlier, final (via tester) |
| AC-02 "count unchanged" | No list route (issue #2). DB-level evidence: `tests/infrastructure/test_feature_database.py::test_postgres_invalid_incidents_do_not_write` (PostgreSQL row counts stay 0), `tests/unit/test_incidents.py::test_missing_fields_leave_no_records`, `test_invalid_input_no_write` | DB tests pass in CI. Not checkable over HTTP until issue #2 is settled |
| AC-02 max length | Waits on issue #3. Only our placeholder (title > 200) is tested at DB level | Open |
| AC-03 (REQ-14) | `test_ac03_unknown_id_get_and_post_return_404[2]`, `test_unknown_incident_get_is_404_with_error_format[2]` | Pass: CI, earlier, final (via tester) |
| AC-04 (REQ-03) | `test_ac04_three_technical_items_are_linked_to_the_incident`, `test_ac04_evidence_is_not_shared_between_incidents` | Pass: CI, earlier, final (via tester) |
| AC-05 (REQ-03) | `test_ac05_evidence_is_stored_and_returned_unchanged[6]`, `test_invalid_evidence_is_rejected_and_not_attached[7]` | Pass: CI, earlier, final (via tester) |
| AC-08, REQ-07 half only | `test_stored_incident_cannot_be_edited_or_deleted[PUT, PATCH, DELETE]` | Pass. Correction history (REQ-06) isn't implemented or tested, so AC-08 as a whole isn't met |
| AC-14 (REQ-13) | `test_health_is_public`, `test_health_body_has_status`, `test_authenticated_route_rejects_bad_key[missing, wrong]`, `test_authenticated_route_accepts_valid_key`, `test_401_uses_error_format[2]`, `test_deployment_uses_https` | Pass: CI (HTTPS skipped), earlier, final via tester, and final keyless by Mohit (7 passed) |
| AC-16 reset | `test_reset_requires_key[2]`, `test_reset_succeeds_and_is_repeatable` (destructive, opt-in); `scripts.check_persistence reset` | Pass: CI, earlier, final (via tester). Per-ID 404 checks only cover the IDs we created. Table-level proof is `tests/infrastructure/test_database.py::test_reset_clears_everything_and_restarts_ids` (CI) |
| AC-16 restart persistence | `scripts.check_persistence create` / restart / `verify` | Local 100/100 (app and full stack). CI 100/100. Earlier `f2b607c` 100/100. **Not run on final** |
| AC-16 response time | `scripts.performance` (200 requests, 100 incidents) | Local 200/200. CI 200/200 (loopback). Earlier `f2b607c` 200/200, p95 61 ms. **Not run on final** |
| AC-06, 07, 09 to 13, 15 | None | Phase 4/5 operations not implemented |

Before any service existed, the AC-14 tests were checked two ways. Against a throwaway local stub with `/health` and key checking, they passed (HTTPS check skipped). Against the bare scaffold with no routes, they failed as expected. Later, against a build without the incident routes, 33 of 35 AC-01 to AC-05 tests failed. The 2 that passed are 404 checks, which a missing route also satisfies.
