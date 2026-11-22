# Phase 5 Gradescope question ownership

This is an assignment and evidence checklist, not a completed Gradescope answer.
Use the actual Phase 5 Gradescope prompts and the Phase 2 pod contract to check
the wording before submission. `README-PHASE5.md` is the work plan. The Phase 3
submission drafts and Phase 4 reports are historical evidence; their deployed
versions and counts must not be reused as Phase 5 results. The generated
`/openapi.json` describes this implementation, not a newly approved shared
contract. Record unknowns as unknowns and date every later observation.

## Q1.1 — Delivered Phase 5 increment

- **Owner:** Astha.
- **Answer:** Describe the increment, users, regulatory context, and each requirement's delivered, partial, or incomplete status.
- **Evidence:** `README-PHASE5.md`, Phase 2 pod contract, `docs/phase5/astha-api-handoff.md`, `docs/phase5/requirement-test-matrix.md`, `app/routes/phase5.py`.
- **Confirm:** The actual users, regulation and Phase 2 REQ IDs; which correction, filing and timeline behaviors work at the submitted commit; evidence for every status.
- **Do not invent:** Regulatory obligations, completed requirements, instructor approval, or deployed behavior from passing local CI.
- **Dependency:** Srihari confirms persistence/deployment facts; Mohit supplies criterion and test evidence.
- **Completion checklist:**
  - [ ] Match scope to the Phase 2 milestone.
  - [ ] Give a status and supporting evidence for every claimed REQ.
  - [ ] Label partial scope explicitly.

## Q1.2 — Comparison with the Phase 2 plan

- **Owner:** Astha.
- **Answer:** Compare planned Phase 5 scope and milestone with what was implemented, deferred, or changed.
- **Evidence:** Phase 2 Section 6.3, `README-PHASE5.md`, `docs/phase4/contract-review.md`, `docs/phase5/contract-and-model-review.md`, recent `integration` history.
- **Confirm:** Exact planned milestone, agreed changes and dates, and any approval required for a scope change.
- **Do not invent:** A Phase 2 promise, pod decision, or instructor approval absent from the source.
- **Dependency:** Srihari confirms infrastructure changes; Mohit supplies test gaps and unresolved contract issues.
- **Completion checklist:**
  - [ ] Cite the original plan.
  - [ ] Explain each material difference.
  - [ ] Mark unapproved changes as pending.

## Q2.1 — Deployment platform and release

- **Owner:** Srihari.
- **Answer:** Give platform, region, runtime, deployed revision, release process, availability and operational limits.
- **Evidence:** `docs/deployment.md`, `docs/submission/q2-deployment.md` (historical), deployment scripts, current cloud revision/health metadata and release logs.
- **Confirm:** Actual Phase 5 API and tester URLs, source SHAs, revision names, region, deployment time and zone, availability observation and limits at that revision.
- **Do not invent:** A Phase 5 deployment, uptime figure, cloud setting, or revision from old Phase 3/4 reports.
- **Dependency:** Astha confirms API scope in the deployed image; Mohit checks tester reachability and version before deployed runs.
- **Completion checklist:**
  - [ ] Map each URL to revision and SHA.
  - [ ] Describe release/rollback from observed configuration.
  - [ ] Date availability and limits evidence.

## Q2.2 — Registry and project documentation

- **Owner:** Astha.
- **Answer:** Identify where the endpoint registry and project documentation were updated and when.
- **Evidence:** `docs/intra-pod-spec.md`, `docs/contract-issues.md`, `docs/setup.md`, registry entry or revision history, project-documentation link and history.
- **Confirm:** Exact registry/document URLs or locations, changed fields, update dates/time zones, editors and the Phase 5 deployment revision they describe.
- **Do not invent:** A registry edit, agreement date, public link, or update timestamp merely because a repository draft exists.
- **Dependency:** Srihari provides final service/tester URLs and revisions; Mohit verifies test-run links and shared-contract wording.
- **Completion checklist:**
  - [ ] Inspect external revision history.
  - [ ] Match entries to deployed versions.
  - [ ] State any update still pending.

## Q2.3 — Operational state and observability

- **Owner:** Srihari.
- **Answer:** Explain persistence, migration, reset, secrets/credentials, logs, metrics and observability for the deployed system.
- **Evidence:** `docs/phase5/srihari-persistence-handoff.md`, `app/models.py`, `app/services/phase5_store.py`, migration `0004`, `docs/deployment.md`, sanitized live log/metric evidence.
- **Confirm:** Fresh/upgraded database behavior, restart and reset results, secret storage/access method, what logs and metrics actually show, and their observation period.
- **Do not invent:** Synthetic-only reset isolation, a deployed secret value, monitoring coverage, or a successful deployed restart from a local test.
- **Dependency:** Mohit supplies restart/reset and performance reports; Astha confirms route and authentication semantics.
- **Completion checklist:**
  - [ ] Reconcile all-data reset with the Phase 5 plan.
  - [ ] Cite migration/restart evidence.
  - [ ] Exclude credentials and sensitive payloads.

## Q3.1 — Common interface and request flow

- **Owner:** Astha.
- **Answer:** List the common-interface operations, implemented status, request/response flow, authentication and errors.
- **Evidence:** Phase 2 Q5.1/Q5.2, `docs/intra-pod-spec.md`, `docs/phase5/astha-api-handoff.md`, `app/routes/`, `app/schemas.py`, generated `/openapi.json`.
- **Confirm:** Exact methods/paths, required fields, success/error codes, authentication order and each operation's status at the submitted SHA.
- **Do not invent:** A new shared operation or approved response field based only on generated OpenAPI.
- **Dependency:** Srihari confirms transaction/persistence flow; Mohit supplies HTTP and OpenAPI check outcomes.
- **Completion checklist:**
  - [ ] Cover every common operation.
  - [ ] Trace one correction and filing request through storage.
  - [ ] Distinguish agreed contract from implementation.

## Q3.2 — Contract version and deviations

- **Owner:** Astha.
- **Answer:** State contract version, changes, pod agreement, deviations and resolution status.
- **Evidence:** Phase 2 pod contract, `docs/intra-pod-spec.md`, `docs/contract-issues.md`, both Phase 5 handoffs, generated `/openapi.json`, dated pod decisions.
- **Confirm:** Which version both pods accepted, who agreed and when, and the exact behavior of every known deviation or ambiguity.
- **Do not invent:** Approval for stale-correction status, filing metadata, duration rounding, holiday rules or reset scope.
- **Dependency:** Srihari checks storage/model consequences; Mohit checks test assertions and reciprocal conformance findings.
- **Completion checklist:**
  - [ ] Version the contract.
  - [ ] List deviations and owners.
  - [ ] Cite actual decisions or mark them open.

## Q4.1 — Runner and interface conformance

- **Owner:** Mohit.
- **Answer:** Describe the runner, target base URL, HTTP response checks, OpenAPI conformance and deviations.
- **Evidence:** `tests/acceptance/client.py`, `tests/acceptance/test_phase5_workflow.py`, `tests/infrastructure/test_phase5_openapi.py`, `tester/`, `docs/phase5/astha-api-handoff.md`.
- **Confirm:** Runner command and version, tested API/tester URL and SHA, observed statuses/bodies, generated schema comparison and any mismatch with the shared contract.
- **Do not invent:** An instructor-provided domain OpenAPI or deployed conformance from CI's loopback service.
- **Dependency:** Astha resolves contract intent; Srihari supplies deployed endpoints and revisions.
- **Completion checklist:**
  - [ ] Record target/version.
  - [ ] Show representative success/error assertions.
  - [ ] Separate generated-schema checks from shared-contract approval.

## Q4.2 — Acceptance mapping and oracles

- **Owner:** Mohit.
- **Answer:** Map Phase 5 ACs to tests, expected outcomes and independent test oracles, including gaps.
- **Evidence:** `docs/phase5/requirement-test-matrix.md`, `tests/fixtures/data/phase5_scenarios.json`, `tests/fixtures/test_phase5_data.py`, Phase 4 fixtures and reports, Phase 5 acceptance tests.
- **Confirm:** Correct REQ/AC IDs, case names/counts, boundary values, no-write checks, provenance of expected values and any partially exercised criterion.
- **Do not invent:** Full criterion coverage from a test name, passing 404 on an absent route, or an oracle derived from production logic.
- **Dependency:** Astha confirms AC interpretation; Srihari confirms DB/restart behavior where HTTP observation is insufficient.
- **Completion checklist:**
  - [ ] Map each claimed AC.
  - [ ] Cite independent expected values.
  - [ ] Identify untested clauses and provisional assertions.

## Q4.3 — Regression and CI evidence

- **Owner:** Mohit.
- **Answer:** Report Phase 3/4/5 regression selections, CI workflow, commands, results and artifacts.
- **Evidence:** `.github/workflows/ci.yml`, `docs/phase5/mohit-acceptance-handoff.md`, `docs/phase4/mohit-final-validation-report.md`, GitHub Actions for the exact submission SHA.
- **Confirm:** CI SHA/link, exact selected/passed/failed/skipped counts, PostgreSQL and app setup, sequential reset steps, JUnit/JSONL availability.
- **Do not invent:** A future CI result or claim old Phase 3/4 deployed results verify the Phase 5 deployment.
- **Dependency:** Srihari confirms migration and deployment SHA; Astha confirms changed API behavior.
- **Completion checklist:**
  - [ ] Recheck CI at final SHA.
  - [ ] Include Phase 3 and 4 regressions.
  - [ ] Explain skips and retain artifact links.

## Q4.4 — Static checks and enforcement

- **Owner:** Mohit.
- **Answer:** State lint, formatting, typing and documentation checks, plus what CI actually enforces.
- **Evidence:** `.github/workflows/ci.yml`, `pyproject.toml`, final CI run, current branch protection/ruleset settings if enforcement is claimed.
- **Confirm:** Exact commands/outcomes, triggering branches, whether failures stop the job, and whether repository rules block merges or deployment.
- **Do not invent:** Required branch protection or a deployment gate because CI itself passes.
- **Dependency:** Srihari confirms deployment process/gates; Astha confirms final commit under review.
- **Completion checklist:**
  - [ ] Quote current check results.
  - [ ] Distinguish failing job from protected merge.
  - [ ] Date settings inspection.

## Q4.5 — Deployed tests and failures

- **Owner:** Mohit.
- **Answer:** Give actual Phase 5 deployed test sessions, counts, coverage basis and classified failures/reruns.
- **Evidence:** `docs/phase5/cross-team-runbook.md`, `docs/test-results/`, tester `/test/setup`, `/test/run`, `/test/report` reports, JUnit/JSONL, deployed `X-App-Commit`.
- **Confirm:** Target/tester URLs and revisions, UTC window, session ID, executed/pass/fail/error/skip counts, coverage denominator, failed request/response and rerun version.
- **Do not invent:** Deployed results or coverage from the passing disposable CI service or Phase 3/4 reports.
- **Dependency:** Srihari supplies deployment and safe reset window; Astha triages API/contract failures.
- **Completion checklist:**
  - [ ] Save raw and structured reports.
  - [ ] Classify each failure.
  - [ ] Mark unrun deployed checks pending.

## Q5.1 — Updated system models

- **Owner:** Srihari.
- **Answer:** Identify and explain updated Phase 5 models and exact diagram file locations.
- **Evidence:** `docs/models/README.md`, Phase 4 model PDF and Markdown, `docs/phase5/contract-and-model-review.md`, Phase 5 schema/migration and any newly produced model files.
- **Confirm:** Which diagrams actually exist, their revision/date, and how they show corrections, filing, timeline, storage and deployment.
- **Do not invent:** A Phase 5 model PDF or claim Phase 4 diagrams have been updated when no new file exists.
- **Dependency:** Astha reviews API/information-flow semantics; Mohit checks model references in the submission.
- **Completion checklist:**
  - [ ] Produce or identify actual files.
  - [ ] Give stable paths and versions.
  - [ ] Review every changed Phase 5 entity/flow.

## Q5.2 — Model-to-implementation consistency

- **Owner:** Srihari.
- **Answer:** Compare each updated model with the implemented API, data relationships, transaction flow and deployment.
- **Evidence:** Phase 5 model files if created, `app/models.py`, `app/services/phase5_store.py`, `app/routes/phase5.py`, migration `0004`, `docs/phase5/srihari-persistence-handoff.md`.
- **Confirm:** Decision correction link, filing uniqueness, event timestamp/order, locks/rollback, reset behavior and any diagram mismatch.
- **Do not invent:** Consistency for a missing diagram or silently resolve the public filing-fields/model discrepancy.
- **Dependency:** Astha checks contract and route models; Mohit supplies test evidence for the modeled behavior.
- **Completion checklist:**
  - [ ] Trace each model element to code.
  - [ ] Record mismatches and fixes.
  - [ ] Recheck deployed architecture at the final revision.

## Q6.1 — Reciprocal cross-team testing

- **Owner:** Mohit.
- **Answer:** Report both testing directions, cases, coverage, failures and coordination evidence.
- **Evidence:** `docs/phase5/cross-team-runbook.md`, dated `docs/test-results/` reports, both testers' session reports, reset-window agreement and target revision records.
- **Confirm:** Our tester on their API and their tester on ours, each target/tester SHA, UTC start/end, session ID, counts, coverage basis and reset owner/window.
- **Do not invent:** Another pod's counts, coverage, credentials, reset window or deployment revision. Phase 3 reciprocal runs are not Phase 5 evidence.
- **Dependency:** Srihari supplies our deployment/revision and coordinates safe access; Astha resolves observed contract failures; other pod supplies its report.
- **Completion checklist:**
  - [ ] Save evidence for both directions.
  - [ ] Identify unrun or unreported direction.
  - [ ] **Keep Q6.1 incomplete or partial if reciprocal Phase 5 testing did not actually occur.**

## Q6.2 — Specification issues and resolution

- **Owner:** Mohit.
- **Answer:** List ambiguities, their test/interoperability impact, owner and agreed or proposed resolution.
- **Evidence:** `docs/contract-issues.md`, `docs/phase5/contract-and-model-review.md`, both Phase 5 handoffs, Phase 4 contract review and dated cross-pod decisions.
- **Confirm:** Status of list/count route, filing fields, stale reference status, duplicate filing, timeline duration, holiday/deadline boundaries and reset scope.
- **Do not invent:** A consensus, date or instructor approval where only a proposal exists.
- **Dependency:** Astha owns contract decisions; Srihari assesses persistence/calendar/reset effects; other pod must agree to shared changes.
- **Completion checklist:**
  - [ ] Tie each issue to observable consequence.
  - [ ] Name decision owner.
  - [ ] Separate agreed resolution from proposed action.

## Q7.1 — Changes and incomplete requirements

- **Owner:** Astha.
- **Answer:** Explain what changed during Phase 5 and which requirements remain incomplete or partial.
- **Evidence:** `README-PHASE5.md`, Phase 2 milestone, `docs/phase5/requirement-test-matrix.md`, `docs/contract-issues.md`, final commit diff and tests.
- **Confirm:** Requirement IDs, status evidence, decisions to defer and any scope/contract approval.
- **Do not invent:** Completion from a passing test that covers only one clause.
- **Dependency:** Srihari confirms operational gaps; Mohit confirms test and deployed-evidence gaps.
- **Completion checklist:**
  - [ ] Reconcile Q1 statuses.
  - [ ] List every incomplete REQ.
  - [ ] Cite exact evidence or blocker.

## Q7.2 — Known limitations and defects

- **Owner:** Srihari.
- **Answer:** Describe reproducible defects, operational limits, impact, workarounds and owners.
- **Evidence:** `docs/phase5/srihari-persistence-handoff.md`, `docs/phase5/contract-and-model-review.md`, final CI/deployed reports, cloud logs and issue tracker.
- **Confirm:** Whether each item is a defect, unresolved contract policy or deployment limit; affected SHA/revision and reproduction evidence.
- **Do not invent:** A production incident, resolved bug or measured performance limit without records.
- **Dependency:** Astha reviews API/contract limitations; Mohit supplies failure classifications and reruns.
- **Completion checklist:**
  - [ ] Classify and date each limitation.
  - [ ] Give impact and owner.
  - [ ] Keep unresolved policies distinct from defects.

## Q7.3 — Next-phase milestones and risks

- **Owner:** Astha.
- **Answer:** Propose milestone and risk adjustments based on actual Phase 5 status.
- **Evidence:** Phase 2 and Phase 5 plans, Q7.1/Q7.2 findings, `docs/phase5/cross-team-runbook.md`, final deployment and cross-team reports.
- **Confirm:** Real remaining work, owners, dependency/order, proposed dates versus agreed dates, and risk triggers.
- **Do not invent:** An agreed schedule, completed deployment or cross-pod sign-off.
- **Dependency:** Srihari estimates deployment/model work; Mohit estimates validation and reciprocal windows.
- **Completion checklist:**
  - [ ] Carry forward incomplete items.
  - [ ] Assign owner and mitigation to each risk.
  - [ ] Label dates as proposed until agreed.

## Q8.1 — Individual GenAI use

- **Owners:** Astha, Srihari and Mohit **each write their own answer**.
- **Answer:** Each person describes their own tools, prompts/workflow, verification, corrections and adherence to agentic principles.
- **Evidence:** That person's own chat/task history, commits, diffs, review notes and test results; the applicable course prompt.
- **Confirm:** Which work the individual actually performed, one real verified correction if requested, and how independent checking changed the result.
- **Do not invent:** Another person's tool use, prompt, correction, verification or personal reflection.
- **Dependency:** Teammates may corroborate shared artifacts; they must not ghostwrite another person's account.
- **Completion checklist:**
  - [ ] Three separate first-person answers.
  - [ ] Link each claim to the writer's own evidence.
  - [ ] Review for invented examples.

## Q9 — Numbered references

- **Owner:** Mohit.
- **Answer:** Compile the numbered reference list and align in-text citations across Q1–Q8.
- **Evidence:** Phase 2 source, course rubric/Gradescope prompt, agreed contract and registry, repository files/commits, CI runs, model artifacts, deployment/cross-team reports, and external sources actually used.
- **Confirm:** Title, author/owner, version, stable URL or path, publication/update date where known, access date for live material, and matching citation number.
- **Do not invent:** A source, access date, quotation, contract version or external approval.
- **Dependency:** Astha and Srihari provide sources cited in their answers; each Q8.1 author identifies their own sources.
- **Completion checklist:**
  - [ ] Number every cited source once.
  - [ ] Resolve missing metadata honestly.
  - [ ] Cross-check each citation against its claim.

## Shared final review

Astha, Srihari and Mohit review the assembled answers against the exact
submission revision before Gradescope submission:

- [ ] Commit hashes for API, tester, model and submission artifacts match the evidence.
- [ ] Deployment revisions map to those hashes and have verified timestamps.
- [ ] Service and tester URLs are reachable and identify the intended revision.
- [ ] Test counts include selected, passed, failed, errored and skipped cases with reasons.
- [ ] Dates have explicit time zones; comparisons use the same time basis.
- [ ] CI links open the run for the stated SHA and required steps passed.
- [ ] REQ and AC IDs match the Phase 2 source and the tests cited for them.
- [ ] Model file locations exist and reflect the submitted implementation.
- [ ] Registry and project-documentation update dates come from actual revision records.
- [ ] Cross-team reset-window evidence identifies both teams and the exclusive time.
- [ ] Reciprocal results exist for each claimed direction, with target/tester revisions and raw reports.
- [ ] Numbered references resolve to the cited source and give real access dates.

If either reciprocal Phase 5 run did not occur, Q6.1 stays incomplete or
partial. Never fill missing evidence with another pod's guessed counts,
coverage, credentials, reset window or deployment revision.
