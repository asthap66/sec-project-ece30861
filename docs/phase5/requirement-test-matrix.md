# Phase 5 requirement-to-test matrix

Owner: Mohit. Reviewed against `README-PHASE5.md`, the Phase 4 source review,
the checked-in intra-pod specification, and generated OpenAPI from this branch.
Astha's API merge `5e97de8` adds correction, filing and timeline paths and
`docs/phase5/astha-api-handoff.md` documents their Q5.1/Q5.2 shapes. The routes
still return 503 until Srihari's adapter is integrated. The course tester
OpenAPI starter mentioned in the Phase 4 review governs `/test/*`, not these
domain paths.

| Phase 5 obligation | Independent input or existing coverage | Status and next assertion |
| --- | --- | --- |
| Original and corrected decisions | `phase5_scenarios.json`; `test_ac08_correction_retains_original_decision` | HTTP test authored: success, current decision, original timeline event. Await adapter to execute. |
| Invalid correction and unknown evidence/incident | `test_ac08_invalid_correction_preserves_state`, missing/foreign/stale/unknown tests | HTTP tests authored for 400, 404, no observable write. Stale reference 400/409 remains contract-open. Await adapter. |
| Correction state transitions | `test_ac15_correction_after_filing_is_conflict` | HTTP test authored for filed-state conflict and unchanged detail/history. Await adapter. |
| Filing eligibility and duplicate | `test_ac15_filing_requires_material_decision`, `test_ac15_duplicate_filing_is_conflict` | HTTP tests authored with no-write checks. Duplicate 409 follows current API design pending pod agreement. Await adapter. |
| Before, on and after deadline | Five fixed `filedAt` instants; `test_ac11_filing_boundary_and_stored_detail` | Fixture oracle validated; HTTP test authored for ON_TIME/LATE, businessDaysLate, FILED detail. Await adapter. |
| Malformed filing | `test_ac11_malformed_filing_is_rejected`, missing-field tests | HTTP tests authored for 400 field errors and no write. Await adapter. |
| Timeline completeness and order | `test_ac12_timeline_complete_ordered_and_recording_timestamps`, empty/unknown test | HTTP tests authored for all event types and IDs, UTC recording order, counts, retained correction and 404. Exact duration rounding remains open. Await adapter. |
| Authentication on new routes | `test_ac14_phase5_routes_require_key` | HTTP tests authored for missing/wrong key and structured 401 on each route. Success tests also prove route behavior after adapter. |
| Unknown resource on new routes | Correction, filing and timeline unknown-ID tests | HTTP tests authored for 404 with valid key. Await adapter. |
| Persistence across restart | `scripts.check_persistence` verifies existing Phase 3 data; fixture describes Phase 5 expectation | Await Phase 5 storage and restart interface; create correction/filing, restart same local app/database, retrieve exact IDs/history. |
| Reset isolation | Phase 3/4 reset tests and fixture expectation | Await Phase 5 records/reset implementation; check synthetic rows gone and unrelated rows remain using disposable local DB. Shared-service reset requires a window. |
| Phase 3 and 4 regressions | Existing Phase 3 acceptance/unit/infrastructure suite; 45 Phase 4 HTTP cases | Retained unchanged; run against disposable PostgreSQL and local API after integration. |
| Generated OpenAPI | `test_phase5_openapi.py` | Four offline checks compare required fields, status codes, authentication and timeline labels against the handoff. |
| CI and tester reporting | `phase5` marker, explicit offline and HTTP selections, JUnit/JSONL | Offline checks enforceable now. Branch adds a blocking HTTP selection for integration after adapter. Existing tester discovers acceptance files automatically. |
| Deployed and reciprocal cross-team testing | Existing tester and runbook | Await integrated deployment revision, target URLs/credentials, mutually agreed reset window; record actual raw and structured reports. |

Offline checks verify scenario data and generated OpenAPI only. The HTTP suite
is written but has no passing integrated run; **Phase 5 operation verification
remains zero**. TODO after Srihari's adapter: run the blocking Phase 5 HTTP
selection against the integrated local service, resolve open contract choices,
then run restart/reset and deployed/cross-team checks before a release claim.
