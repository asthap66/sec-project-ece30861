# Q6 Cross-team readiness (draft)

Lead: Mohit. Working checklist: `docs/test-results/cross-team.md`.

## What we can offer the other team

- **Deployed service:** https://incident-api-356019173418.us-central1.run.app, HTTPS, commit visible in the `X-App-Commit` header. Our own suite passes 48/48 against it (2026-10-18).
- **Test key:** a synthetic key, shared over a private channel. It's never in git or the report.
- **Test runner:** `tests/acceptance/`. It only needs Python 3.12 and `uv`, plus `BASE_URL` and `API_KEY`. Destructive `/reset` tests only run with `ALLOW_DESTRUCTIVE_TESTS=1`.
- **Fixtures:** `tests/fixtures/data/*.json`, plain JSON in the pod contract's field format.
- **Our choices where the contract is silent:** listed in `docs/submission/q3-interface-conformance.md` (error codes, auth-first precedence, placeholder length limits, IDs restart at `INC-001` after reset).

## Status

| Direction | Status |
| --- | --- |
| Our tests → their service | 2026-10-18, non-destructive: **45 passed, 0 failed**, 3 reset tests skipped on purpose ([details](../test-results/2026-10-18-cross-team-ours-on-theirs.md)). Reset tests and AC-16 wait for an agreed window |
| Their tests → our service | Not run yet. URL and key sent 2026-10-18 |

## Open with the other team

- A time window for runs that call `POST /reset`, so neither team wipes the other's data mid-run.
- `GET /incidents` (contract issue #2) and field length limits (issue #3).

Results from both directions, including failures and who owns each one, will be recorded in `docs/test-results/`.
