# Cross-team testing (Q6)

Owner: Mohit. Both directions have to be attempted and recorded, including failures and who owns each issue.

## What we need from the other team

- [ ] Their deployed HTTPS base URL.
- [ ] A shared synthetic test API key, exchanged privately. Never put it in git, chat screenshots or the report.
- [ ] An agreed time window for runs that call `POST /reset`, so neither team wipes the other mid-run.
- [ ] Their position on the open contract questions: `GET /incidents` (issue #2) and length limits (issue #3).

## What we give them

- Our deployed base URL and test key, once Srihari's deployment is up.
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
| Our tests → their service | Not started. Waiting on their URL and key |
| Their tests → our service | Not started. Waiting on our deployment |
