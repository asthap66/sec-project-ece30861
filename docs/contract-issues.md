# Contract issues and open questions

Owner: Mohit. Record each decision, who agreed to it, and the date it was resolved.

Source checked so far: the pod's common contract in *Phase 2 - Pod.pdf*: Q5.1 interface table, Q5.2 schemas, valid/invalid examples, and AC-01 to AC-16.

| # | Issue | Status | Decision |
| --- | --- | --- | --- |
| 1 | Obtain the instructor-provided OpenAPI spec, confirm its version, and check how it relates to the Phase 2 common contract. | Open | Not found in any course material available to us (2026-10-16). Request it from the course staff/pod. Until it arrives, the Phase 2 pod contract is the working reference. |
| 2 | Phase 2 AC-02 mentions listing incidents, but the Phase 2 interface table omits `GET /incidents`. Does the route exist? | Confirmed conflict; proposal awaiting pod agreement | See [Issue 2](#issue-2-get-incidents) below. |
| 3 | Agree exact field length limits (and the whitespace policy) for incident and evidence fields. | Open | The contract says only `title` and `description` have a "maximum length agreed by both teams". Every other string is just "non-empty". The numbers and the whitespace-only policy are still unagreed. |
| 4 | Confirm error response formats, and the precedence between validation and authentication failures (e.g. invalid body with a missing API key). | Partly resolved | The contract fixes the format: every error is `{"error": "ERROR_CODE", "message": "..."}`. A missing or invalid key → 401, unknown resource → 404, invalid state → 409, edit/delete attempts → 405. **Precedence is still unspecified.** Working assumption in `tests/acceptance/test_ac14_security.py`: auth is checked before resource lookup (unknown ID without a key → 401). |

## Issue 2: GET /incidents

**Evidence (Phase 2 - Pod.pdf):**

- AC-02's action is "POST each one, then **list all incidents**". Its expected result says "the incident **count is unchanged**".
- AC-16's action is "Restart the service and **GET the incidents**". Its expected result says "All 100 incidents remain after the restart" and "**no incidents remain** after the reset".
- The Q5.1 interface table defines only `GET /health`, `POST /incidents`, `GET /incidents/{incidentId}` (and its sub-resources), and `POST /reset`. There is no collection `GET /incidents`.

Without a list route, neither AC-02's "count unchanged" check nor AC-16's "no incidents remain" check can be automated. This is a gap in a contract both teams share, so one team can't settle it alone.

**Proposed resolution (needs agreement from the pod and the other team):**

Add `GET /incidents` to the common contract:

- It requires `X-API-Key` and returns 401 otherwise.
- It returns `200 OK` with a JSON array of Incident objects, each with the same shape as `GET /incidents/{incidentId}`.
- After `POST /reset`, it returns an empty array.

That is the smallest addition that makes AC-02 and AC-16 testable as written. Ordering, pagination, and filters stay out of scope unless the pod asks for them.

**Fallback if the pod declines:** change AC-02 to check that each rejected POST returns 400 naming the bad field, without the count check. Change AC-16 to re-GET each of the 100 IDs it created before the restart, and confirm with 404s after the reset. Either way, the acceptance tests won't call `GET /incidents` until this row is marked agreed.

**Decision:** _pending. Record who agreed and the date._
