# Supplied contract review — 2026-11-01

Historical source review; see [November 2 integrated validation](mohit-final-validation-report.md)
for current passing implementation, date-range limitation and unresolved pod choices.
The missing-route statement below describes the original baseline.

Mohit received and read the following source PDFs after the initial test commit:

- `student-facing-spec.docx.pdf`: Cross-team Testing Interface, including the
  OpenAPI 3.1.1 tester starter version 0.4.2. This governs tester/system testing
  endpoints; it does not define the domain decision/calendar rules.
- `Phase 2 - Pod (1).pdf`: shared v1.0 requirements, Q3.2 Models 1–4,
  AC-01–16, Q5.1/Q5.2 domain contract and Q6.2/Q6.3 milestones. Models on
  pages 7–8 were rendered and visually inspected because they are images.
- `Phase 2 Part 2 (1).pdf`: team architecture, append-only decisions, derived
  status and on-demand calendar design. This is not a replacement API contract.

These were supplied from Mohit's Downloads folder, not added to git. The
Gradescope text supplied with them confirms the milestone split. This review
supersedes missing-source and provisional-schema statements from the initial
handoff. No additional domain OpenAPI document was supplied or assumed.

## Resolved from the actual sources

| Prior uncertainty | Source and implemented assertion |
| --- | --- |
| NOT_MATERIAL state | Model 1 and Q5.2 Incident.status explicitly use NOT_MATERIAL |
| New MATERIAL after NOT_MATERIAL | Model 1 has this ordinary-decision transition; added test checks new current decision and ID |
| Decision/detail fields | Q5.2 defines decisionId, decision, determinedAt, decidedBy, rationale, evidenceIds, deadline; detail example nests them under currentDecision |
| Null deadline | Q5.2: Decision.deadline is null for non-material; DeadlineStatus.deadline is null when not applicable |
| Due-date boundary | Model 3: PENDING when Eastern as_of date is on/before due date, OVERDUE afterward; tests cross the Eastern midnight boundary |
| Concrete businessDays counts | Model 3 example: 2026-09-28 determination, 2026-10-02 deadline; Oct 1 pending by 1, Oct 5 overdue by 1, Oct 6 late by 2. Tests assert the corresponding no-filing status counts |
| Invalid decision enum | Q5.2 invalid example fixes INVALID_DECISION and message `decision must be MATERIAL or NOT_MATERIAL`; test uses the example's PROBABLY_MATERIAL input |
| Required text and errors | Q5.2 requires nonempty decidedBy/rationale; Model 4 requires 400 + field name for invalid body fields; tests now assert both |
| Acceptance-date oracle | AC-09 and AC-10 explicitly specify all five requested deadlines; manual fixtures now cite the actual artifact |
| Phase scope | Q6.2 is human decisions/deadlines; Q6.3 retains corrections, filings, history and timelines |
| Tester contract | Starter and full interface align with existing setup/run/report; report summaries remain additive, coverage means exercise, not success |

## Remaining issues requiring agreement

1. **Calendar years:** AC-09/10 explicitly use 2025 (and January 2026), while
   Model 3's shared holiday list contains only 2026 and 2027. Keep the explicit
   acceptance dates; Srihari and both teams must agree how to extend calendar
   support to 2025. Do not silently infer a complete 2025 holiday list.
2. **businessDays beyond examples:** date status boundary is resolved, but the
   general counting interval, pre-determination as_of, and exact due-date zero
   convention should be made explicit. Tests assert concrete model counts and
   status boundaries without inventing every edge count.
3. **NOT_APPLICABLE businessDays:** Q5.2 calls this field integer but does not
   specify its value when no deadline applies. Tests assert status and null
   deadline; do not impose zero or null for businessDays without agreement.
4. **Future as_of:** optional as_of exists; future-time rejection or simulation
   semantics are not explicit. Current tests use historical explicit times.
5. **Duplicate evidence IDs**, numeric text limits, and error codes/messages
   other than the provided enum example are not fully specified.
6. **Determination equal to discovery:** REQ-05 says reject before discovery;
   Model 2 says determination is after discovery. Resolve equality before an
   exact equality test. Current valid fixtures are strictly after discovery.
7. **Filing representation:** Model 2 uses filing_date and filed_by, whereas
   Q5.2 uses filedAt/accessionNumber. Deferred to Phase 5 owners, not implemented
   by Mohit here. Filing-dependent AC-11/15 and correction-history AC-08 remain
   partial/deferred.

The original defect handoff remains: HTTP incident equality checks observable
no-write behavior, but cannot detect orphan decision rows; Srihari must add
transactional database checks. Missing routes still fail the baseline selection.
