# Phase 5 contract and model review

Reviewed on 2026-11-21 from this branch. The working production code is the
merged `origin/integration` revision `2825e67`; `origin/main` alone was an
older scaffold with the new plan. `app.openapi()` lists decision and deadline
operations but no correction, filing or timeline operation. No Phase 5
migration or model exists. Existing Phase 4 diagrams in `docs/models/` show
MATERIAL_PENDING_FILING and explicitly defer filing and corrections.

The Phase 4 source review records that the Phase 2 v1.0 Q5.2 filing fields
include `filedAt` and `accessionNumber`, while its Model 2 labels internal
`filing_date` and `filed_by`. This discrepancy is unresolved; this branch does
not choose a public schema or change a model. The Phase 2 Model 3 Eastern
calendar-date boundary and the explicit 2025-10-03 deadline provide the four
fixed filing instants in the scenario fixture. Its `ON_TIME`/`LATE` labels
come from the Phase 5 plan. A final decision on timestamp semantics, event
types/order, correction identity, and duplicate/conflict responses is needed
before route-level assertions can be written.

Review the new models when Astha and Srihari deliver them:

1. Compare the public correction, filing and timeline shapes with the final
   shared contract and generated OpenAPI; record differences and agreement.
2. Check that original decisions and evidence remain visible after a
   correction, and that generated IDs and timestamps are stable after restart.
3. Confirm timeline ordering and timestamp provenance against stored rows.
4. Confirm the filing state and timeliness rule at both sides of Eastern
   midnight, including 2025 calendar support.
5. Confirm reset removes only agreed synthetic data, including new dependent
   records, and migration upgrades an existing Phase 4 database.

No Phase 5 PDF or replacement diagram is asserted complete by this review.

## Astha API merge review

Integration commit `5e97de8` adds generated OpenAPI paths and the public
schemas listed in `astha-api-handoff.md`. Four offline contract checks now
compare required request/response fields, route status codes, event labels,
and API-key documentation with that handoff. The old “no Phase 5 route” note
above describes the pre-merge baseline. Routes still return 503 until the
storage adapter arrives; the schemas do not prove persisted behavior.

The unresolved public questions are stale correction reference status (400 or
409), duplicate filing status, observable supersession, precise timeline
duration semantics, and filing/calendar edges. HTTP tests assert exact
documented fields, current 409 duplicate behavior provisionally, and retained
history; stale correction reference accepts the two contract-open client-error
statuses while still requiring a structured error and unchanged state.

## Srihari persistence merge review

Integration commit `9e32887` adds migration 0004, correction links and filing
rows, a filing-aware incident snapshot, and a database-backed timeline ordered
by recording time. Its handoff reports fresh/upgraded migration tests,
transaction and race tests, a process restart, reset, and a passing trial of
Mohit's 34 HTTP cases. The earlier 503 statement describes the pre-adapter
baseline. The remaining model questions concern filed deadline status,
filing-time sanity, duration rounding, stale reference response, and reset
scope. No new Phase 5 model PDF is claimed complete here.
