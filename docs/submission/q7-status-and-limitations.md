# Q7 Status and limitations

Lead: Mohit (consolidating; Srihari and Astha check their areas). This draft matches `docs/submission/mohit-gradescope-ready.md`, which is the version to paste. Raw results are in `docs/test-results/`.

## Version facts

| Fact | Value | How it was checked |
| --- | --- | --- |
| Final deployed system (cover page) | `f551649` at https://incident-api-356019173418.us-central1.run.app | `X-App-Commit` header, 2026-10-19 01:55 UTC |
| Our tester | https://incident-tester-356019173418.us-central1.run.app | `GET /health` returned 200 |
| CI run on the deployed commit | [run 39182054445](https://github.com/asthap66/sec-project-ece30861/actions/runs/39182054445), `f551649`, success | GitHub Actions |
| Latest CI run on `integration` | [run 39185515218](https://github.com/asthap66/sec-project-ece30861/actions/runs/39185515218), `a520f25`, success | GitHub Actions |
| Older deployments with results | `ed5f449` (acceptance), `f2b607c` (AC-16 persistence and performance) | Q2 and `docs/test-results/2026-10-18-deployed.md` |

**Changes between `f2b607c` and `f551649`:**
- Deployment scripts and the `X-App-Commit` header.
- The `/docs` Authorize button.
- The course testing interface: `/test/setup`, `/test/report`, migration 0002 and per-session coverage via `APP_COVERAGE=1`.
- Max instances changed to 1.

The incident and evidence routes are the same, but this isn't a docs-only difference.


## Q7.1 Delivered and incomplete work

**Delivered:**
- Create and retrieve incidents with status `OPEN`, UTC timestamps and `INC-001` IDs (REQ-01, AC-01). Invalid input gets a 400 naming the field, and nothing is saved (REQ-02, AC-02, apart from the list-based count).
- Evidence attachment with all four categories, recorded time, unknown incident giving 404 (REQ-03, AC-03, AC-04, AC-05). Edit and delete give 405 (REQ-07).
- API-key auth on everything except `/health`, served over HTTPS (REQ-13, AC-14). `{error, message}` errors and `POST /reset` (REQ-14).
- Data persists in Cloud SQL across restarts (REQ-15, AC-16 on `f2b607c`).
- The course testing interface on our system, plus a deployed tester that runs our 48-test suite. It passed 48/48 against both our system and the other team's.
- CI that runs static checks, 212 tests, the acceptance suite and an AC-16 smoke test on every push.

**Incomplete:**
- Phase 4 decision workflow and deadlines: REQ-04, REQ-05, REQ-08, REQ-09, REQ-10; AC-06, AC-07, AC-09, AC-10, AC-15. Not started.
- Corrections, filing, timeline (REQ-06, REQ-11, REQ-12; AC-08 history half, AC-11 to AC-13). Planned for Phase 5.
- AC-16 persistence and timing on the final deployment `f551649`. Not re-run.
- Their tester's run against our system (no report yet), and cross-team AC-16 (restart and timing) in both directions.
- Pod decisions on the list route (issue #2) and length limits (issue #3).

## Q7.2 Known limitations

| ID | Affected REQ / operation | Severity | Workaround | Target phase |
| --- | --- | --- | --- | --- |
| L1 | AC-02 count check, AC-16 "no incidents remain" (no `GET /incidents`) | Medium | Per-ID 404 checks over HTTP, plus DB row-count tests in CI | Phase 4, after pod decision |
| L2 | REQ-02 length limits (`POST /incidents`) | Medium | Placeholders 200/5000; tell the other team our limits | Phase 4, after pod decision |
| L3 | AC-16 on final version `f551649` not measured | Medium | Results on `f2b607c` (same incident/evidence routes) and CI smoke runs on `f551649` | Before Phase 4 work starts |
| L4 | Their tester's report against our system not received | High for Q6 grading | Our tester passed 48/48 against them; our interface is live for theirs | Before submission if possible |
| L5 | `/test/report` coverage held in memory on one instance | Low | `max-instances 1`; restart clears coverage only, not data | Phase 4 |
| L6 | `test_feature_database.py` line 44 compares the DB clock with the host clock | Low (tests only) | Passes in CI. Failed locally once with a measured 3 to 4 s host/container clock gap | Phase 4 (Astha adds a tolerance) |
| L7 | No enforced merge or deploy gate | Medium | Team habit of merging and deploying only green commits | Phase 4 (needs branch protection, which this private repo plan doesn't offer, or a public repo) |
| L8 | `HEAD /health` gives 405 | Low | Use GET | Phase 4, if needed |

## Q7.3 Comparison with the Phase 4 plan and changes needing pod agreement

Our Phase 2 plan (Q6.2) set Phase 4 to deliver:
- The human materiality decision workflow and state rules.
- The four-business-day deadline calculator with the holiday list.
- The deadline-status endpoint.
- Expanded fixtures, covering REQ-04, REQ-05, REQ-08, REQ-09 and REQ-10 and validated with AC-06, AC-07, AC-09, AC-10 and state-conflict tests.

That plan still holds. Phase 3 delivered what was planned (REQ-01 to REQ-03, REQ-13, and most of REQ-14/15), so Phase 4 can build on working storage, auth and deployment.

**Added to Phase 4:**
- The leftover Phase 3 items: AC-16 on the final version, the other team's report on our system, and the length-limit and list-route decisions.
- Upkeep of the course testing interface, which wasn't in the Phase 2 plan.

**Updated risks:**
- **Deadline arithmetic around holidays and Eastern Time** is still the highest-risk logic. The AC-09 and AC-10 fixtures should be written first.
- **Shared-deployment resets:** the `/test/setup` and `/reset` calls on a shared deployment can wipe the other team's runs.
- **Divergent choices on open contract points:** lengths, extra fields and error codes could make cross-team runs fail even when both systems are correct.
- **No enforced CI gate:** a bad commit could be deployed.

**Changes that need pod agreement (not decided yet):**
1. Add `GET /incidents` or reword AC-02/AC-16.
2. Exact max lengths and the whitespace policy.
3. Whether unknown fields are ignored or rejected.
4. A shared list of error codes.
5. A schedule for destructive test windows.
6. The shared holiday list for AC-10.
