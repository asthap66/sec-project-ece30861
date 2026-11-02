# Mohit Phase 4 Gradescope draft

Editorial notes (do not paste): Prepared November 2, 2026 UTC. Phase 4 exact
question text is unavailable locally; labels follow Mohit's supplied assignment
and historical submission headings. Q4.1–4.4, Q6.2, Q7.2, Q8.1 are evidence-backed
with explicit limits. Q4.5 and Q6.1 remain pending external execution. Update
Q4.3/Q4.4 with the final validation PR CI link in the evidence report. All older
missing-route/clock failures are historical, not current integrated defects.

## Q4.1 — Test interface, configuration and conformance

Our tester exposes POST /test/setup, POST /test/run and GET /test/report. Setup
accepts target_url, obtains a unique session ID, prepares the selected system,
and returns 201 when ready. Run executes the suite once and stores its report;
report retrieval does not rerun tests. Direct pytest runs select the system
through BASE_URL and its X-API-Key credential through API_KEY. The deployed
tester uses ALLOWED_TARGETS and TARGET_API_KEYS or TARGET_API_KEY for target
credentials, separate from any tester access controls. No source edits are
needed to change approved targets.

On November 2, 2026 UTC, read-only GET /health returned 200 and {"status":"OK"}
from both registered services. The API URL is
https://incident-api-356019173418.us-central1.run.app and the tester URL is
https://incident-tester-356019173418.us-central1.run.app. The API reported
X-App-Commit e9dd257 and its OpenAPI still omitted the Phase 4 routes. Tester
source SHA and both deployment revisions were unavailable. These observations
confirm reachability, not deployment of the integrated increment. Testing-interface
shapes are supported by local tests; a Phase 4 deployed session is still pending.

The contract basis is pod specification v1.0 plus the separate course testing
interface. Local Phase 4 assertions pass. Remaining deviations or unapproved
choices include the 2025–2027 calendar range, extension of holiday data to 2025,
NOT_APPLICABLE businessDays=0, duplicate evidence handling and provisional text
limits. A passing implementation test does not establish pod approval.

## Q4.2 — Acceptance mapping and independent oracles

For REQ-04/05 and AC-06, test_ac09_material_decision_calendar checks successful
material decisions and retrieved fields; test_ac06_not_material_has_no_applicable_deadline
checks NOT_MATERIAL; test_ac06_invalid_decision_no_observable_write and
test_ac06_invalid_references_and_future check invalid fields, timestamps and
evidence ownership, with incident observations before and after rejection.
For REQ-04/AC-07, test_ac07_evidence_does_not_decide is supplemented by source
inspection: evidence storage does not create decisions, and status follows an
explicit human POST rather than an inference from evidence.

For REQ-09, test_ac09_material_decision_calendar covers AC-09's standard date
and AC-10's weekend/holiday dates, plus offset and midnight cases. Expected
deadlines and manually enumerated days are stored in phase4_deadlines.json
from the pod's AC-09/10; no production calculator generates the oracle. For
REQ-10/AC-11's no-filing portion, test_ac11_deadline_status_without_filing,
test_ac11_model3_business_days and test_ac11_eastern_due_date_boundary use
fixed historical as_of values and Model 3 counts. For REQ-08/AC-15,
test_ac15_second_ordinary_decision_preserves_original checks 409 without changes,
and test_ac15_material_decision_after_not_material checks the defined transition.

Authentication/resource checks are test_ac14_phase4_authentication and
test_ac03_phase4_unknown_incident. test_ac16_reset_removes_decided_incident
covers public reset observations; separate local database inspection verifies
all project tables empty. Existing Phase 3 tests retain incident/evidence,
validation, authentication, errors, health, reset and no-edit/delete coverage.
Filing-dependent AC-11/15 and correction-history AC-08 remain partial/deferred.
No claim of complete AC-08/11/15 coverage is made.

## Q4.3 — Regression prevention and CI

I independently tested integrated source 50f1c53 using disposable PostgreSQL
and a local HTTP server. All 323 original non-acceptance tests passed, the full
HTTP selection had 92 passes and one local HTTPS skip, and the explicit Phase 4
selection passed all 45 tests. A subsequent reporting-mapping regression test
raises the non-acceptance count to 324. The chronology regression verifies the
actual historical discovery sent by setup and preserves shared fixtures.

CI retains Phase 3 checks, disposable PostgreSQL, migrations, persistence and
performance scripts. The final validation PR removes Phase 4 continue-on-error,
so failures now fail the job while JUnit/JSONL evidence is still uploaded.
CI outcome and URL are recorded in docs/phase4/mohit-final-validation-report.md;
use that final run rather than historical green informational runs. Jobs are
isolated per workflow run; destructive tests run sequentially within the job.
This does not isolate separate testers writing to a shared deployment.

## Q4.4 — Static checks and enforcement

Ruff lint, Ruff format checking, strict mypy and git diff --check passed locally.
GitHub Actions runs static checks before tests, and the changed Phase 4 step
propagates pytest's nonzero exit code. I did not change repository settings.
The integration branch-protection query returned 404 and the rulesets query
returned an empty list, so enforced merge blocking was not established. A failed
job and a repository rule preventing merges are separate claims. CI completion
is recorded in the final validation report; deployment remains a separate action.

## Q4.5 — Full suite against the deployed version

[PENDING: Srihari's Phase 4 API and tester source SHAs/revisions, authorized
exclusive synthetic-data/reset window, and the resulting deployed suite report.]
The November 2 read-only API check still reported e9dd257 with no Phase 4 routes.
I therefore have no Phase 4 deployed full-suite result to report. Local results
are 92 HTTP passes, one local HTTPS skip, and 45/45 in the Phase 4 selection;
they are not deployed evidence. Local performance used 100 incidents and 200
sequential requests: all were under one second, no errors, p95 49.3 ms. Exact
local decision fields and derived state/deadline survived a process restart;
known IDs returned 404 after reset and all four project tables were empty.
These are local persistence/reset observations, not Cloud Run measurements.

## Q6.1 — Cross-team results

[PENDING: Phase 4 reciprocal reports for our tester against the other team's
system and their tester against ours, with both app/tester SHAs, session IDs,
UTC timestamps, outcomes, coverage definitions, failures and rerun evidence.]
No Phase 4 reciprocal reports were found in the repository or reviewed PR
comments. Historical October Phase 3 reports do not establish Phase 4 success.
Both directions require a coordinated exclusive reset window. Code coverage
must come from system instrumentation or be unavailable with a reason;
component coverage needs an agreed component definition. Criterion exercise
is not conformance, and the test pass rate is not a coverage measurement.

## Q6.2 — Shared specification issue and proposed plan

AC-02 requires checking that incident count is unchanged and AC-16 requires
checking that no incidents remain, but v1.0 defines no list/count operation.
Public known-ID retrieval checks cannot prove those global properties; local
DB counts provide different evidence. The proposal is for the larger pod to
choose by November 8, 2026 between adding GET /incidents with agreed semantics
and formally revising the criteria to defined ID-based checks. I found no
recorded decision approving either option. This remains a proposal; any scope
reduction requires the applicable instructor sign-off. We will record the
participants, decision and date, update the shared contract/tests together,
and rerun both implementations after agreement.

## Q7.2 — Current limitations and defects

The integrated local decision/deadline workflow passes its tests; the previous
missing-route and host-versus-database timestamp failures are resolved in this
source. They are not current production defects. Deployment and reciprocal
Phase 4 validation remain pending. Corrections, filings and timeline/summary
features remain Phase 5, so correction history and filing-dependent criteria
are not fully verified.

The calculator restricts MATERIAL determination dates and applicable as_of
calendar calculations to 2025–2027, including days traversed when counting.
It does not reject historical incident discovery dates: the 2020 setup succeeds.
NOT_MATERIAL/no-decision status bypasses calendar range checking. The shared
contract does not explicitly authorize the range restriction, so DATE_OUT_OF_RANGE
for otherwise valid earlier MATERIAL determinations is a limitation/deviation
for Srihari and the pod to review. Holiday version us-federal-2025-2027.v1,
NOT_APPLICABLE businessDays=0, duplicate evidence order, general counting edges,
future as_of, discovery/determination equality and numeric text limits need
pod confirmation where v1.0 does not settle them. The list/count issue remains
open. No approval is inferred from implementation or passing tests.

## Q8.1 — Mohit's GenAI use

I used Codex to assist with HTTP acceptance tests, synthetic fixtures, CI,
reporting, repository inspection and draft documentation. The outputs were
checked with automated tests and static checks. A concrete correction was that
generated tests paired a September 2026 discovery fixture with 2025 determination
dates. Teammates identified that these supposed successes would violate the
contract. I corrected setup to copy the fixture and use an earlier historical
discovery timestamp, preserving the independent expected deadlines, and added
a regression check for chronology and fixture isolation. The initial missing-route
failures had masked the invalid setup: 404 responses had not demonstrated valid
inputs. I report measured results and remaining gaps rather than treating
generated code or an initial baseline run as proof of correctness.

## Reference suggestions for Astha's Q9

Pod Phase 2 v1.0: REQ-01–15, Models 1–4, AC-01–16, Q5 interface and Q6 milestones.
Student-facing Cross-team Testing Interface: setup/run/report, outcomes and
coverage; OpenAPI starter 0.4.2. Phase 2 Part 2: append-only decisions and derived
state/deadline design. Repository source at 50f1c53 and final validation PR,
including independent fixtures, contract review and evidence report. Use the
actual GitHub Actions run link from that report. Holiday provenance is documented
in app/holidays.py as observed US federal holidays under 5 U.S.C. 6103/OPM;
that provenance is not itself pod approval. Retain original SEC/RFC references
where used, without representing this software as legal advice.
