# Phase 5 requirement-to-test matrix

Owner: Mohit. Reviewed against `README-PHASE5.md`, the Phase 4 source review,
the checked-in intra-pod specification, and generated OpenAPI from this branch.
The generated document currently has decisions and deadline status, but no
corrections, filing, or timeline path. A final Phase 5 domain OpenAPI artifact
or Astha's agreed schema handoff has not been provided. The course tester
OpenAPI starter mentioned in the Phase 4 review governs `/test/*`, not these
domain paths.

| Phase 5 obligation | Independent input or existing coverage | Status and next assertion |
| --- | --- | --- |
| Original and corrected decisions | `phase5_scenarios.json` original/corrected human decisions; Phase 4 decision tests | Fixture validated. Await correction request/response schema; assert success, retained original and current decision. |
| Invalid correction and unknown evidence/incident | Invalid scenario names; existing Phase 4 decision invalid-reference tests | Await correction validation semantics; assert error envelope/status and no observable write. |
| Correction state transitions | Original MATERIAL and corrected NOT_MATERIAL fixture | Await agreed state table, especially correction after filing; assert no unauthorized transition. |
| Filing eligibility and duplicate | Invalid scenario names | Await filing schema and conflict status; assert ineligible and duplicate writes leave detail/history unchanged. |
| Before, on and after deadline | Four fixed `filedAt` instants around 2025-10-03 Eastern date | Fixture validated against documented date boundary. Await filing response shape; assert ON_TIME/LATE and incident state. |
| Malformed filing | Invalid scenario name | Await required fields/validation rules; assert documented 400 shape and no write. |
| Timeline completeness and order | Five ordered semantic events in fixture | Fixture validated. Await timeline event types, timestamp meaning and ordering rule; assert incident/evidence/decision/correction/filing events and retained prior decision. |
| Authentication on new routes | Existing `ApiClient` supports missing/wrong/valid keys | Await routes; assert 401 and structured error for each new operation. Generic middleware-only 401 is insufficient. |
| Unknown resource on new routes | Existing unknown-ID fixture | Await routes; assert contract 404 with valid key after route existence is proven. |
| Persistence across restart | `scripts.check_persistence` verifies existing Phase 3 data; fixture describes Phase 5 expectation | Await Phase 5 storage and restart interface; create correction/filing, restart same local app/database, retrieve exact IDs/history. |
| Reset isolation | Phase 3/4 reset tests and fixture expectation | Await Phase 5 records/reset implementation; check synthetic rows gone and unrelated rows remain using disposable local DB. Shared-service reset requires a window. |
| Phase 3 and 4 regressions | Existing Phase 3 acceptance/unit/infrastructure suite; 45 Phase 4 HTTP cases | Retained unchanged; run against disposable PostgreSQL and local API after integration. |
| CI and tester reporting | `phase5` marker, fixture tests, CI JUnit/JSONL selection | Enforced for fixture tests now. Add route tests to marker after contract handoff; failures must remain blocking. Existing tester discovers acceptance files automatically. |
| Deployed and reciprocal cross-team testing | Existing tester and runbook | Await integrated deployment revision, target URLs/credentials, mutually agreed reset window; record actual raw and structured reports. |

The fixture checks verify test inputs only. They are **not** acceptance tests,
and the current Phase 5 operation coverage is zero. TODO after the API handoff:
write HTTP tests with the exact route payloads and success/error schemas, then
run every row above against the integrated local service before a release claim.
