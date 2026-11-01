# Phase 4 execution and cross-team preparation

Read [the report](mohit-phase4-report.md) for mappings and executed results, and
[the source review](contract-review.md) for resolved rules and remaining ambiguities.
The local selection is `uv run pytest -m phase4`. Full HTTP suite is
`uv run pytest tests/acceptance`; existing regression is
`uv run pytest -m 'acceptance and not phase4'`. No parallel pytest workers:
reset tests and ID reuse require sequential execution against one target.

Before any shared run, Mohit must request the target URL/version, privately
exchanged target API key, confirmation of the reviewed Phase 2 v1.0 sources and unresolved holiday-year policy, an
exclusive synthetic-data window, reset permission, restart operator and
contact, and reciprocal tester details. This document sends no messages.

Reset-window checklist:

1. Both teams explicitly agree start/end/timezone and a single reset owner.
2. Confirm no competing tester, manual writer, restart or CI targets the service.
3. Record both application and tester SHAs, migration head and target URL.
4. Use synthetic inputs only; retain no secrets in evidence.
5. Run restart persistence before reset; save failures before subsequent resets.
6. Release the window and exchange sanitized results, including failed/skipped cases.

For direct CLI, set `BASE_URL` and `API_KEY` privately; the client uses
`X-API-Key`. No source edits needed. Set `ALLOW_DESTRUCTIVE_TESTS=1` only in
that authorized window (it allows reset; other tests also create records).
Save results outside tracked paths:

```sh
mkdir -p /tmp/phase4-evidence
export TESTER_RESULTS_FILE=/tmp/phase4-evidence/events.jsonl
export GIT_COMMIT="$(git rev-parse HEAD)"
uv run python -m pytest tests/acceptance -p tester.pytest_plugin \
  --junitxml=/tmp/phase4-evidence/results.xml
```

Exit status must be retained; do not pipe through a command that conceals it.
JUnit records outcomes/reasons and durations; JSONL records plan, timestamp,
timezone, target, tester SHA and actual total duration. Retrieve target version
from `X-App-Commit` on GET /health when available, otherwise label unavailable.
Do not calculate component/system conformance percentages from test counts.

The deployed tester already discovers all acceptance files and packages all
fixtures. Srihari configures `ALLOWED_TARGETS`, `TARGET_API_KEYS` (URL-to-key
JSON) or fallback `TARGET_API_KEY`. These target credentials are distinct from
any external access controls placed on the tester. Preserve the tester's
POST /test/setup body `{ "target_url": "<approved base URL>" }`, then
POST /test/run with returned `session_id`, then GET /test/report with query
`session_id`. Setup and suite resets require the same coordinated window.
No deployed tester was invoked for this work.

Failure handoff template:

- Test node ID, REQ/AC and partial scope:
- Target URL, app/tester commits, migration, UTC time:
- Setup POST /incidents body and returned ID (sanitized):
- Evidence POST body and returned ID:
- Minimal failing method/path/body, replacing credentials with `<private key>`:
- Expected status/body and source section:
- Actual status/body, before/after incident GET observations:
- Reproducibility, reset interference, owner and next verification:

Received-results template (other team's suite against ours):

- Their suite SHA/version, our app SHA/URL, window/timezone:
- Planned/executed/passed/failed/errored/skipped, reasons:
- Attach original sanitized reports and minimal reproductions:
- Criteria fully verified versus partially exercised and deferred:
- Specification disagreement versus implementation defect:
- Owner, corrective action, rerun evidence and remaining limits:

No Phase 4 reciprocal results exist yet. Historical Phase 3 results remain in
`docs/test-results/`; they are not evidence for the new functionality.
