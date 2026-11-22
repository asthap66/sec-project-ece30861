# Phase 5 requirement-to-test matrix

Owner: Mohit. Reviewed against `README-PHASE5.md`, the Phase 4 source review,
the checked-in intra-pod specification, and generated OpenAPI from this branch.
Astha's API merge `5e97de8` adds correction, filing and timeline paths and
`docs/phase5/astha-api-handoff.md` documents their Q5.1/Q5.2 shapes. Srihari's
integration merge `9e32887` connects the PostgreSQL adapter. The course tester
OpenAPI starter mentioned in the Phase 4 review governs `/test/*`, not these
domain paths.

| Phase 5 obligation | Independent input or existing coverage | Status and next assertion |
| --- | --- | --- |
| Original and corrected decisions | `phase5_scenarios.json`; `test_ac08_correction_retains_original_decision` | HTTP test authored and reported passing in Srihari's trial merge; verify on final integration CI. |
| Invalid correction and unknown evidence/incident | `test_ac08_invalid_correction_preserves_state`, missing/foreign/stale/unknown tests | HTTP checks cover structured 400/404 and unchanged detail/history. Stale reference 400/409 remains contract-open. |
| Correction state transitions | `test_ac15_correction_after_filing_is_conflict` | HTTP check covers filed-state conflict and unchanged detail/history. |
| Filing eligibility and duplicate | `test_ac15_filing_requires_material_decision`, `test_ac15_duplicate_filing_is_conflict` | HTTP checks cover no-write behavior. Duplicate 409 follows current API design pending pod agreement. |
| Before, on and after deadline | Five fixed `filedAt` instants; `test_ac11_filing_boundary_and_stored_detail` | Fixture oracle validated; HTTP checks cover ON_TIME/LATE, businessDaysLate, FILED detail. |
| Malformed filing | `test_ac11_malformed_filing_is_rejected`, missing-field tests | HTTP checks cover 400 field errors and no write. |
| Timeline completeness and order | `test_ac12_timeline_complete_ordered_and_recording_timestamps`, empty/unknown test | HTTP checks cover all event types and IDs, UTC recording order, counts, retained correction and 404. Exact duration rounding remains open. |
| Authentication on new routes | `test_ac14_phase5_routes_require_key` | HTTP checks cover missing/wrong key and structured 401 on each route. |
| Unknown resource on new routes | Correction, filing and timeline unknown-ID tests | HTTP checks cover 404 with valid key. |
| Persistence across restart | `test_reset_and_restart_with_phase5_data`; Srihari's process-restart probe | Database-backed TestClient restart and separate uvicorn process restart reported passing in Srihari's handoff; rerun after final merge. |
| Reset isolation | `test_reset_and_restart_with_phase5_data`; `POST /reset` and `/test/setup` | All project records are removed per REQ-14; synthetic-only isolation conflicts with this and remains a pod decision. Shared-service reset needs a window. |
| Phase 3 and 4 regressions | Existing Phase 3 acceptance/unit/infrastructure suite; 45 Phase 4 HTTP cases | Retained unchanged; run against disposable PostgreSQL and local API after integration. |
| Generated OpenAPI | `test_phase5_openapi.py` | Four offline checks compare required fields, status codes, authentication and timeline labels against the handoff. |
| CI and tester reporting | `phase5` marker, explicit offline and HTTP selections, JUnit/JSONL | Both selections are blocking on integration after merge. Existing tester discovers acceptance files automatically. |
| Deployed and reciprocal cross-team testing | Existing tester and runbook | Await integrated deployment revision, target URLs/credentials, mutually agreed reset window; record actual raw and structured reports. |

Srihari's handoff records a passing 34-case local HTTP trial of this test
branch with his adapter. The final integration CI run and Mohit's deployed and
cross-team evidence remain pending. Contract choices above remain provisional;
passing tests do not settle them.
