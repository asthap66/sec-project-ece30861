# Cross-team testing interface

Owner: Srihari. Implements the course's "Cross-team Testing Interface"
(student-facing spec): our **system** exposes `POST /test/setup` and
`GET /test/report`, and our **tester** is a separate service with
`POST /test/setup`, `POST /test/run` and `GET /test/report`.

## Registry values

| Field | Value |
| --- | --- |
| System base URL | https://incident-api-356019173418.us-central1.run.app |
| Tester base URL | https://incident-tester-356019173418.us-central1.run.app |
| Intra-pod spec | Phase 2 pod specification (common contract Q5.1–Q5.3, AC-01 to AC-16) |
| Access | Every system endpoint except `/health` needs the shared key in `X-API-Key`. The key is shared by private message only, never in the registry, repo or chat. The tester's endpoints are open; it only targets approved URLs. |

## Our system: `/test/setup`, `/test/report`

- `POST /test/setup {"session_id", "setup": {}}` → `201 {"session_id"}`.
  Resets the database to an empty baseline (no incidents, no evidence, IDs start
  at `INC-001` / `EVD-001`) and starts code coverage for the session. A session ID
  can be used once; reusing it is `409`. Takes well under a second.
- `GET /test/report?session_id=...` → `200 {"session_id", "coverage": {"code": ...}}`
  with the lines of the `app` package executed by project requests since that
  setup. Reading the report doesn't change the numbers. Unknown session: `404`.
- One session is active at a time: a new setup resets the data and starts a new
  measurement. Project requests carry no session ID. **Tell us before a run** so
  two teams don't reset the system at the same time.
- Errors on `/test/...` are `{"message", "source": "system"}` (plus `error` on 401).

## Our tester

- `POST /test/setup {"target_url"}` → `201 {"session_id"}` (a new UUID). It calls
  the target's `/test/setup` with that ID. The target URL must be an approved pod
  system URL (no query, no `/test` suffix); anything else is `400`. If the system's
  setup fails, its status, message and source are passed back unchanged; if the
  system can't be reached, `500` with `source: communication`.
- `POST /test/run {"session_id"}` → `200` with the full report when the suite
  finishes. A session runs once; running it again is `409`. If the run aborts
  (time limit, crash), `500` and the report keeps the results so far: the test in
  progress is `error` (source `tester`), the rest `skip`.
- `GET /test/report?session_id=...` → the stored report; `409` before the run.
- What it runs: our acceptance suite, `tests/acceptance` (48 tests,
  destructive tests included). Outcomes are `pass`, `fail`, `error` (source
  `system` for 5xx answers, `communication` for timeouts/connection errors, `tester`
  for our own failures) and `skip`.
- Coverage in the report:
  - **code:** taken from the target's `/test/report`
  - **component:** null, because the pod spec defines no component list
  - **system:** acceptance criteria exercised, out of AC-01 to AC-16
- Time limits: setup 60 s, run 600 s (Cloud Run request timeout 900 s).

## Adding the other team's system

Their key goes in Secret Manager, never in the repo:

```sh
printf '%s' '{"<their base url>": "<their key>"}' | \
  gcloud secrets create tester-target-keys --data-file=- --project ece30861-project-62ca4b
PROJECT_ID=ece30861-project-62ca4b \
ALLOWED_TARGETS=https://incident-api-356019173418.us-central1.run.app,<their base url> \
  scripts/deploy_tester_gcp.sh
```

(Use `gcloud secrets versions add` if the secret already exists.) Targets with
no entry there use our own `api-key`.

## Running it

```sh
T=https://incident-tester-356019173418.us-central1.run.app
curl -s -X POST $T/test/setup -H 'Content-Type: application/json' \
  -d '{"target_url": "https://incident-api-356019173418.us-central1.run.app"}'
curl -s -X POST $T/test/run -H 'Content-Type: application/json' -d '{"session_id": "<id>"}'
curl -s "$T/test/report?session_id=<id>"
```

## Live check (2026-10-18, commit `f551649`)

Our tester against our deployed system:

- Setup: `201` in 0.8 s.
- Report before the run: `409`.
- Run: `200` in 5.9 s. **48 pass** with unique test IDs. Coverage: code 135/522
  lines, component null with a reason, system 8/16 (AC-01, 02, 03, 04, 05, 08, 14, 16).
  "System" counts ACs with at least one test run, not ACs fully met: AC-08 is
  only its REQ-07 edit/delete half, and AC-16 is only the reset tests.
- Running again: `409`. The stored report matches the run response.
- Non-approved target: `400`.
- Our system's `/test/setup` without a key: `401` with `source: system`.
