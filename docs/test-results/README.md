# Test results

Owner: Mohit. Feeds submission Q4 and Q6.

Record real runs only. For each run, include: commit/tag, date, target (local, our deployment, or the other team's deployment), totals, failures, skips, and issue owners.

## Runs

| Date | Target | Result |
| --- | --- | --- |
| 2026-10-16 | Local Docker Compose (`f6b8df6`) | [AC-16 and acceptance, all passing](2026-10-16-local-ac16.md) |

No deployed or cross-team runs have happened yet. CI also runs the acceptance suite and an AC-16 smoke test (persistence across an app restart, reset, response time) against an app inside the CI job on every push. Those runs are regression checks, not recorded results.
