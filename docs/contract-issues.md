# Contract issues and open questions

Owner: Mohit. Record each decision, who agreed to it, and the date it was resolved.

| # | Issue | Status | Decision |
| --- | --- | --- | --- |
| 1 | Obtain the instructor-provided OpenAPI spec, confirm its version, and check how it relates to the Phase 2 common contract. | Partially clarified | User supplied Phase 2 - Pod.docx on October 16, 2026. Q1.3 identifies pod specification v1.0; Q5 defines the common JSON API. The instructor OpenAPI file is still absent. |
| 2 | Phase 2 AC-02 mentions listing incidents, but the Phase 2 interface table omits `GET /incidents`. Does the route exist? | Open | Confirmed discrepancy in the supplied document: AC-02 uses listing; Q5.1 omits a list route. No extra endpoint added. |
| 3 | Agree exact field length limits (and the whitespace policy) for incident and evidence fields. | Open | Q5.2 explicitly leaves title/description maximum lengths to team agreement; no numeric limits are provided. Existing nonblank checks preserve submitted text per the user's instructions. |
| 4 | Confirm error response formats, and the precedence between validation and authentication failures (e.g. invalid body with a missing API key). | Specified; integration pending | Q3.2 Model 4: authentication, endpoint/method, incident existence, body validation, workflow state. Q5 requires error/message JSON; REQ-02 and Model 4 require the bad field name for 400. Authentication/global 404/405 handling remains Person 1's task. Exact incident/evidence error codes are not enumerated. |

These are observations from the supplied specification, not newly negotiated pod
decisions. For Phase 3 only incident/evidence operations are implemented; Q6.1
retains database, auth, reset, deployment, and persistence verification obligations.

Model 2 uses internal `reported_by` while Q5 uses public `reporterName`; the
database adapter must map these names. `created_at` is internal and is absent
from Q5 incident retrieval JSON. Later-phase document discrepancies (including
2025 acceptance dates versus the Model 3 2026–2027 holiday list) need agreement
before deadline work; no deadline functionality is implemented here.
