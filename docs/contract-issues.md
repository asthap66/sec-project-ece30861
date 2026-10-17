# Contract issues and open questions

Owner: Mohit. Record each decision, who agreed to it, and the date it was resolved.

Sources checked: the pod's common contract in *Phase 2 - Pod.pdf* and the user-supplied *Phase 2 - Pod.docx*: Q3.2 models, Q5.1 interface table, Q5.2 schemas, valid/invalid examples, and AC-01 to AC-16.

| # | Issue | Status | Decision |
| --- | --- | --- | --- |
| 1 | Obtain the instructor-provided OpenAPI spec, confirm its version, and check how it relates to the Phase 2 common contract. | Partially clarified | User supplied Phase 2 - Pod.docx on October 16, 2026. Q1.3 identifies pod specification v1.0; Q5 defines the common JSON API. The instructor OpenAPI file is still absent. |
| 2 | Phase 2 AC-02 mentions listing incidents, but the Phase 2 interface table omits `GET /incidents`. Does the route exist? | Confirmed conflict; proposal awaiting pod agreement | AC-02 uses listing; Q5.1 omits a list route. See [Issue 2](#issue-2-get-incidents) below. No extra endpoint added. |
| 3 | Agree exact field length limits (and the whitespace policy) for incident and evidence fields. | Open | Q5.2 explicitly leaves title/description maximum lengths to team agreement; no numeric limits are provided. Existing nonblank checks preserve submitted text. Integration now reuses shared provisional storage limits (title 200, description 5000, reporterName/source 500) so oversized inputs return 400; these numbers are not pod-approved and need coordinated config/schema/migration review. |
| 4 | Confirm error response formats, and the precedence between validation and authentication failures (e.g. invalid body with a missing API key). | Specified; wired into feature routes | Q3.2 Model 4: authentication, endpoint/method, incident existence, body validation, workflow state. Q5 requires error/message JSON; REQ-02 and Model 4 require the bad field name for 400. Feature routes now use shared authentication/error infrastructure and check evidence parent existence before parsing the body. Real-app tests exercise authentication-first ordering with an injected repository; PostgreSQL execution remains unverified locally. Exact incident/evidence error codes are not enumerated. |

These are observations from the supplied specification, not newly negotiated pod
decisions. For Phase 3 only incident/evidence operations are implemented; Q6.1
retains database, auth, reset, deployment, and persistence verification obligations.

Model 2 uses internal `reported_by` while Q5 uses public `reporterName`; the shared ORM and API both use reporter_name, mapped to reporterName in JSON. `created_at` is internal and is absent
from Q5 incident retrieval JSON. Later-phase document discrepancies (including
2025 acceptance dates versus the Model 3 2026–2027 holiday list) need agreement
before deadline work; no deadline functionality is implemented here.

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
