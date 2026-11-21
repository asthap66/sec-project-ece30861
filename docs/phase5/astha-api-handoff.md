# Astha Phase 5 API handoff

Base: integration `4e239a4`. The shared Phase 2 v1.0 source was read from
`Phase 2 - Pod.docx` in the user's Downloads; Q5.1/Q5.2 specify the following
public shapes. The instructor tester OpenAPI discussed in the Phase 4 review
is not a domain API contract. The repository does not contain a newer domain
OpenAPI. No Phase 5 SQLAlchemy adapter or migration is implemented here.

- `POST /incidents/{incidentId}/corrections`: request `correctsDecisionId`,
  `decision`, `determinedAt`, `decidedBy`, `rationale`, `evidenceIds`;
  201 response `decisionId`, `status`, `deadline`.
- `POST /incidents/{incidentId}/filing`: request `filedAt`, `accessionNumber`;
  201 response `filingId`, `status`, `timeliness`, `businessDaysLate`.
- `GET /incidents/{incidentId}/timeline`: 200 response `incidentId`, `events`,
  `evidenceCounts`, `discoveryToDeterminationDays`. Each event has `eventType`,
  `recordedAt`, `referenceId`; event labels are `INCIDENT_CREATED`,
  `EVIDENCE_ADDED`, `DECISION_RECORDED`, `DECISION_CORRECTED`,
  `FILING_RECORDED`. Counts contain `technical`, `businessImpact`, `legal`,
  `other`. Filing detail has `filingId`, `filedAt`, `accessionNumber`,
  `timeliness`, `businessDaysLate`.

## Persistence integration for Srihari

Implement `Phase5Repository` in `app/services/phase5.py`, retaining the existing
`DecisionRepository` interface. `transaction(incident_id)` must lock and read a
fresh complete `IncidentDetail` (including filing), return 404 for a missing
incident, serialize writes, commit once after successful exit, and roll back
all changes on any exception including commit failure. Its transaction exposes:

- `append_decision` as today.
- `append_correction(data) -> str`: append a new decision with a new public ID,
  atomically persist the link identifying its superseded predecessor and keep
  the predecessor and evidence links; make the replacement current.
- `append_filing(data, timeliness, business_days_late) -> str`: append the
  filing and ensure subsequent snapshots expose the filing and FILED status.
- `get_timeline(incident_id) -> IncidentTimeline`: return a consistent snapshot
  with all event types, true recording timestamps and stable recording order,
  evidence counts and the agreed duration; unknown incident returns 404. Do not
  sort by user-entered `determinedAt`, `collectedAt`, or `filedAt`.

Adapt the incident retrieval dependency to use the same Phase 5-aware repository,
so detail returns the corrected current decision and filing. Replace the
`get_phase5_repository` unavailable dependency with that real adapter on the
request's shared session. The current routes intentionally return 503 with a
valid API key; no working storage or timeline is claimed. Existing Phase 4
repository remains unchanged. The repository and integration must coordinate
reset and migrations, preserving existing data and history.

## Open questions for the pod

- Q5.2's public filing fields are `filedAt`/`accessionNumber`; Model 2 also
  refers to `filing_date`/`filed_by`. Confirm their mapping and whether the
  latter is required beyond the public shape.
- Q5.2 mandates a current decision reference but does not specify whether a
  stale or unknown reference is 400 or 409. This implementation provisionally
  returns 400; agree before cross-team assertions.
- The timeline schema provides event references but no `superseded` field,
  while AC-08 says the old decision is marked superseded and asks for history.
  Agree how clients observe that fact without silently adding a public field.
- Clarify discovery-to-determination rounding, timezone/date convention and
  which decision applies after correction; the adapter must not guess. Also
  agree stable order when different records share recording timestamps.
- Agree whether future or pre-determination filing timestamps are invalid;
  Q5.2 specifies an offset and nonempty accession only, so no extra restriction
  is imposed. Confirm duplicate and out-of-order semantics and error precedence.
- The shared calendar's 2025 holiday extension and general late-day counting
  need pod confirmation. Late on a nonbusiness day can have zero business
  days late while still LATE. REQ-14 specifies reset clears all data, while the
  Phase 5 plan requests synthetic-only isolation; reconcile these before reset.

## Mohit handoff

The contract shapes and status expectations above come directly from Q5.1/Q5.2;
independent timeline, HTTP and persistence acceptance checks remain blocked on
Srihari's adapter and the listed agreements. Unit tests use a transactional
in-memory test double only. Filing classification delegates to the shared
calendar and has fixed independent expected examples. Do not interpret the
registered routes or 503 responses as completion, and retain Phase 3/4
regressions and independent fixtures when integrating.
