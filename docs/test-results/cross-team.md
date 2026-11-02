# Cross-team testing (Q6)

Owner: Mohit. Both directions have to be attempted and recorded, including failures and who owns each issue.

## What we need from the other team

- [x] Their deployed HTTPS base URL: https://incident-clock.onrender.com (tester: https://incident-clock-tester.onrender.com).
- [x] A shared synthetic test API key, exchanged privately. Never put it in git, chat screenshots or the report.
- [ ] A written schedule for runs that call `POST /reset` or `/test/setup`. None exists yet. On 2026-10-19 their tester's resets clashed with our AC-16 run, which is why we need one.
- [ ] Their position on the open contract questions: `GET /incidents` (issue #2) and length limits (issue #3).

## What we give them

- Our deployed base URL, https://incident-api-356019173418.us-central1.run.app, and the test key (private channel only; see `docs/submission/q2-deployment.md`).
- The shared fixtures in `tests/fixtures/data/`, as plain JSON in the AC-01 format.
- The commands below. Our suite only needs Python 3.12 and `uv`.

## Running our suite against their service

```sh
export BASE_URL=https://<their-service> API_KEY=<their test key>
uv run pytest -m acceptance                       # non-destructive
ALLOW_DESTRUCTIVE_TESTS=1 uv run pytest -m acceptance    # only inside the agreed reset window
uv run python -m scripts.performance              # response time
```

Record each run in this folder with the date, their commit or version if they share it, totals, every failure (expected vs actual, plus a reproducible request), and whether the failure points to their implementation, ours, or the shared spec.

## Status

| Direction | Status |
| --- | --- |
| Our tests → their service | Non-destructive run 2026-10-18: [45 passed, 0 failed, 3 reset tests skipped](2026-10-18-cross-team-ours-on-theirs.md). Reset tests and AC-16 wait for an agreed window |
| Their tests → our service | **Run seen in our logs** (2026-10-19 02:07:17 to 02:09:17 UTC). Their report hasn't been received |
| Our tester → their service | Done 2026-10-18 by Srihari: **48 pass, 0 fail, 0 skipped**; code 325/406 (their basis), system 8/16. See `docs/cross-team-testing.md` |
