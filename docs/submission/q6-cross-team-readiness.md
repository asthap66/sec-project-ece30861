# Q6 Cross-team readiness

Lead: Mohit. Working checklist and raw results: `docs/test-results/cross-team.md`.

Both teams built from the same specification, the Phase 2 pod contract v1.0. The other team's service publishes its copy at `/openapi.yaml`. It lists the same operations, fields and rules we built from, so neither team has added anything to the shared interface.

## Testing in both directions

| Direction | What happened | Result |
| --- | --- | --- |
| Our tests → their service (https://incident-clock.onrender.com) | 2026-10-18: our acceptance suite, run non-destructively | **45 passed, 0 failed, 3 skipped.** The skips are the `/reset` tests, left out on purpose so we didn't wipe their data. [Details](../test-results/2026-10-18-cross-team-ours-on-theirs.md) |
| Their tests → our service (https://incident-api-356019173418.us-central1.run.app) | We gave them our URL, our test runner (`tests/acceptance/`) and a key, over a private channel | **Not run.** Their tester (https://incident-clock-tester.onrender.com) works through the course test interface, which needs `/test/setup` and `/test/report` on the target system. We haven't implemented those endpoints, so their tester can't target us yet |

Our suite only checks the outside behaviour of an operation, so the 45 passes are evidence that their AC-01 to AC-05 and AC-14 behaviour matches the contract as we read it. That includes AC-14's HTTPS check. They aren't evidence about AC-16 (persistence, reset, response time), which we haven't run against them.

## Specification ambiguities and their status

| Topic | What the contract says | Our service | Their service | Status |
| --- | --- | --- | --- | --- |
| Course test interface (`/test/setup`, `/test/report`) | Not in the pod contract | Not implemented | Implemented. `/test/report` needs a `session_id` | **Open.** We haven't found the course document that defines these endpoints. It's the main reason only one direction has run |
| `GET /incidents` (issue #2) | Not defined, though AC-02 and AC-16 refer to listing incidents | Not implemented (405) | Not in their spec | Both left it out, so the services agree. The AC-02 count check and AC-16's "no incidents remain" are checked one ID at a time instead |
| Field length limits (issue #3) | Not specified | Title ≤ 200, description ≤ 5000 (placeholders) | Only "not empty"; maximums left open | **Open.** Longer valid input would be accepted by them and rejected by us with a 400 |
| Unknown extra fields | Not specified | Ignored | Not specified in their spec | Unconfirmed. No failures seen |
| Error code names | Only `{error, message}` is required | `UNAUTHORIZED`, `NOT_FOUND`, `METHOD_NOT_ALLOWED`, `INVALID_<FIELD>` | `UNAUTHORIZED`, `NOT_FOUND` seen; also `INVALID_SESSION_ID` | Our tests check the shape, not the exact code. Unconfirmed whether their tests check exact codes |
| Health body | `{status: string}` | `"OK"` | `"ok"` | Both are valid |
| Reset coordination | `/reset` clears all data | — | — | **Open.** No time window has been agreed for destructive runs in either direction |

## Still open

These are recorded as they stand at submission, not as resolved.

- Implement the course test interface on our service, or confirm with the other team another way for their tester to run against us.
- Agree length limits and the reset window with the other team, then run our `/reset` tests and AC-16 scripts against them.
- Record their results against our service, including failures and who owns each one, once they can run.
