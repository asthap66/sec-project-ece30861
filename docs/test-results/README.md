# Test results

Owner: Mohit. Feeds submission Q4 and Q6.

Record real runs only. For each run, include: commit/tag, date, target (local, our deployment, or the other team's deployment), totals, failures, skips, and issue owners.

## Runs

| Date | Target | Result |
| --- | --- | --- |
| 2026-10-16 | Local Docker Compose (`f6b8df6`) | [AC-16 and acceptance, all passing](2026-10-16-local-ac16.md) |
| 2026-10-18 | Our deployment, earlier versions (`ed5f449` / `f2b607c`) | [48 passed acceptance; 100/100 persisted; 200/200 under 1 s](2026-10-18-deployed.md) |
| 2026-10-18 | Our deployment, final version `f551649` | [Tester run by Srihari: 48 pass. Keyless subset by Mohit: 7 passed, 41 skipped. AC-16 below](2026-10-18-deployed-f551649.md) |
| 2026-10-19 | Our deployment, final version `f551649` | [AC-16 pass: 100/100 persisted, 200/200 under 1 s (p95 65 ms), reset cleared all 100. First attempt invalid (other team's tester reset us mid-run)](2026-10-19-ac16-deployed.md) |
| 2026-10-18 | Other team's deployment (incident-clock) | [Our suite: 45 passed, 0 failed, 3 skipped (reset tests, on purpose)](2026-10-18-cross-team-ours-on-theirs.md) |

CI also runs the acceptance suite and an AC-16 smoke test (persistence across an app restart, reset, response time) against an app inside the CI job on every push. Those runs are regression checks, not recorded results.
