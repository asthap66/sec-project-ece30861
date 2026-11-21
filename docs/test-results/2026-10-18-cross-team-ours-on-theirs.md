# 2026-10-18: our acceptance suite against the other team's service

Owner: Mohit. **Target: the other team's deployment**, https://incident-clock.onrender.com. Their key was shared privately. It isn't recorded here.

## Conditions

| | |
| --- | --- |
| Date | 2026-10-18, about 8:30 PM local |
| Our suite | `tests/acceptance/` at `38972ff` (`integration`) |
| Their version | Not shared |
| Mode | Non-destructive: `ALLOW_DESTRUCTIVE_TESTS` was not set, because no reset window has been agreed |
| Client | A laptop over the public internet |

## Result

**45 passed, 0 failed, 3 skipped** (`pytest -m acceptance`).

- The 3 skips are the `/reset` tests in `test_system_endpoints.py`. They were skipped on purpose so we wouldn't wipe their data.
- All the AC-01 to AC-05 and AC-14 tests passed: create/retrieve, invalid input gives 400 naming the field, unknown IDs give 404, evidence attachment, 405 on edit/delete, missing/wrong key gives 401, HTTPS.
- Their `/health` returns `{"status":"ok"}`, lowercase. Ours returns `"OK"`. The contract only requires a string, so both pass.

## Not yet run

- The `/reset` tests and the AC-16 scripts (persistence, response time). Both reset the target, so they wait for an agreed window.
- Their tests against our service.

The run left some synthetic test incidents (titles and descriptions from `tests/fixtures/data/`) in their database.
