# Q6 Cross-team readiness

Lead: Mohit. This draft matches `docs/submission/mohit-gradescope-ready.md`, which is the version to paste. Raw results are in `docs/test-results/`.

## Version facts

| Fact | Value | How it was checked |
| --- | --- | --- |
| Final deployed system (cover page) | `f551649` at https://incident-api-356019173418.us-central1.run.app | `X-App-Commit` header, 2026-10-19 01:55 UTC |
| Our tester | https://incident-tester-356019173418.us-central1.run.app | `GET /health` returned 200 |
| CI run on the deployed commit | [run 39182054445](https://github.com/asthap66/sec-project-ece30861/actions/runs/39182054445), `f551649`, success | GitHub Actions |
| Latest CI run on `integration` | [run 39185515218](https://github.com/asthap66/sec-project-ece30861/actions/runs/39185515218), `a520f25`, success | GitHub Actions |
| AC-16 on the final version | Srihari, 2026-10-19 02:10 to 02:11 UTC, Mohit's scripts | `docs/test-results/2026-10-19-ac16-deployed.md` |
| Older deployments with results | `ed5f449` (acceptance), `f2b607c` (AC-16) | Q2 and `docs/test-results/2026-10-18-deployed.md` |

**Changes between `f2b607c` and `f551649`:**
- Deployment scripts and the `X-App-Commit` header.
- The `/docs` Authorize button.
- The course testing interface: `/test/setup`, `/test/report`, migration 0002 and per-session coverage via `APP_COVERAGE=1`.
- Max instances changed to 1.

The incident and evidence routes are the same, but this isn't a docs-only difference.


## Q6.1 Cross-team testing in both directions

| Direction | Status | Result | Issues / owners |
| --- | --- | --- | --- |
| Our suite → their system (https://incident-clock.onrender.com) | Done 2026-10-18, about 20:25 EDT, by Mohit. Non-destructive (`ALLOW_DESTRUCTIVE_TESTS` unset), suite at `38972ff` | **45 passed, 0 failed, 3 skipped.** The skips are our 3 reset tests, left out because no reset window was agreed | None from the passing tests. Their health returns `"ok"` and ours `"OK"`; both meet `{status: string}`. Our run left synthetic incidents in their database |
| Their tester → our system | **Run seen, report not received.** Our Cloud Run logs show their tester (on Render) running a session on our system from 02:07:17 to 02:09:17 UTC on 2026-10-19: `/test/setup`, repeated `/reset`, then `/test/report`. They haven't sent us the report, so we can't state their pass/fail counts | **PENDING** (the report) | Their run overlapped with our AC-16 run and invalidated our first attempt; see Q6.2 |
| Our tester → their system | Done 2026-10-18 by Srihari through our deployed tester (session `7c8dd57b-c179-48f1-8a92-465b4d8063be`). Their key is kept in our Secret Manager. This run included our 3 reset tests | **48 pass, 0 fail, 0 skipped.** Setup 201 in 0.8 s, run 200 in 9.9 s | None found |
| Our tester → our system (self-check of the interface) | Done 2026-10-18 by Srihari | 48 pass; coverage as in Q4.5 | n/a |

**Coverage available:**
- **Our tester on our system:** code 135/522 lines; component null; system 8/16 ACs exercised.
- **Our tester on their system:** code 325/406 lines (reported by their `/test/report`; their basis counts lines run at import, ours doesn't, so the two code numbers can't be compared); component null; system 8/16 ACs with at least one test run.
- **Our earlier direct suite run on their system:** no code-coverage figure (it didn't use the testing interface). It exercised AC-01 to AC-05, the REQ-07 half of AC-08, and AC-14.
- **Their tester on our system:** the run happened (seen in our logs); their coverage and pass/fail numbers are in their report, which is **PENDING**.

## Q6.2 Specification ambiguities

| Ambiguity | Effect | Resolution or proposed plan |
| --- | --- | --- |
| No instructor OpenAPI spec | Each team could build its own idea of the interface | Resolved inside our team (issue #1): build from the Phase 2 pod contract v1.0. The other team's `/openapi.yaml` is a copy of the same contract, so we line up in practice |
| AC-02 says "list all incidents" and AC-16 says "GET the incidents", but there's no list route (issue #2) | Neither team can check "count unchanged" or "no incidents remain" through the API | Proposed to the pod, not agreed: add `GET /incidents`, or reword the ACs. Until then we check per ID and use DB-level tests for "nothing saved" and "tables empty" |
| Max lengths for title/description are left open (issue #3) | Their schema only requires non-empty strings; we reject title > 200 and description > 5000. Long valid input could pass on theirs and fail on ours | Proposed: agree on numbers with the other team. Ours are placeholders, and boundary tests wait until then |
| Unknown extra fields aren't covered | One side might reject what the other accepts | We ignore them. Not yet raised with the other team |
| Error code names: only `{error, message}` is required | Tests checking exact codes could fail across teams | Our tests check the shape, not the code. We share our code list (Q3) and propose comparing |
| `/reset` and `/test/setup` clear all data on a shared deployment | This happened: on 2026-10-19 the other team's tester reset our system 24 times while our AC-16 script was creating incidents, and our first attempt read 92/100. Our rerun after their session passed | No schedule was agreed beforehand. Proposed: agree a written time slot before any destructive run, in both directions |
| The course testing interface sits outside the pod contract | Error format for `/test/*` differs (`{message, source}`); "session" meaning is up to each team | Both teams implemented it. Ours: one active session, setup resets the data, reusing an ID gives 409 (`docs/cross-team-testing.md`) |
