# Q2 Deployment and operation (draft)

Lead: Srihari.

Items marked **TODO** need the real deployment. Fill them with what actually
happened, not what was planned (README §9).

## Host and runtime

- **Host:** TODO (not deployed yet).
- **Runtime:** one Docker image (`Dockerfile`): Python 3.12, FastAPI served by
  Uvicorn, dependencies installed from the locked `uv.lock`. Runs as a
  non-root user.
- **Database:** PostgreSQL 16, separate from the app, so data outlives app
  restarts and redeploys.
- **HTTPS:** TODO (terminated by the host / reverse proxy; the app trusts the
  proxy's forwarded headers, `--proxy-headers`).

## Deployed URL

- **Base URL:** TODO (`https://...`)
- **Public endpoint:** `GET /health` → `200 {"status": "OK"}`
- Every other endpoint needs the shared test key in `X-API-Key`.

## Commit mapping

Every response carries an `X-App-Commit` header with the git commit the
running image was built from (`docker build --build-arg GIT_COMMIT=$(git rev-parse --short HEAD)`).
To check what is deployed:

```sh
curl -sI https://<base-url>/health | grep -i x-app-commit
```

- **Deployed commit / tag:** TODO

## Secrets

- `DATABASE_URL` and `API_KEY` are set as environment variables on the host,
  never in git, images, logs, or this report. `.env` is git-ignored;
  `.env.example` has placeholders only.
- The API key is compared in constant time; a blank configured key rejects every
  request instead of disabling authentication.
- **How the test key is shared with the other team:** TODO (agree a private
  channel; don't paste it in the shared repo or the report).

## Persistence, startup and restart

- On start, the container applies pending database migrations
  (`alembic upgrade head`), then starts the API (`scripts/start.sh`).
  Already-applied migrations are skipped, so this is safe on every restart.
- Data stays until `POST /reset`, which clears evidence and incidents in one
  transaction and restarts the IDs at `INC-001`.
- **Restart procedure:** TODO (the host's restart command).
- **Restart check:**
  - Local, 2026-10-16: reset, inserted one incident, `docker compose restart app`;
    `INC-001` was still present after the restart and gone after the reset.
  - Deployed: TODO (with Mohit).

## Logging

One line per request: request ID, method, path, status, duration, and any
record IDs in the path. Headers (which carry the API key) and request/response
bodies (which carry incident details) are never logged. The request ID is also
returned in the `X-Request-Id` header, so a client-side failure can be matched
to its log line.

Sanitized excerpt from a **local** run (2026-10-17, commit `4887b57`):
`/health` without a key, `/reset` without and with a key, an unknown
incident ID, and a delete attempt.

```
2026-10-17 21:05:41,067 INFO app.requests request_id=c695f017490d method=GET path=/health status=200 duration_ms=19.5 ids=-
2026-10-17 21:05:41,090 INFO app.requests request_id=7963624cf79f method=GET path=/health status=200 duration_ms=1.3 ids=-
2026-10-17 21:05:41,109 INFO app.requests request_id=9e25b648cba7 method=GET path=/health status=200 duration_ms=1.6 ids=-
2026-10-17 21:05:41,125 INFO app.requests request_id=79d6a7806b6b method=POST path=/reset status=401 duration_ms=0.5 ids=-
2026-10-17 21:05:41,227 INFO app.requests request_id=4672a90c66c8 method=POST path=/reset status=200 duration_ms=88.8 ids=-
2026-10-17 21:05:41,241 INFO app.requests request_id=35fbce3147ed method=GET path=/incidents/INC-404 status=404 duration_ms=0.2 ids=INC-404
2026-10-17 21:05:41,251 INFO app.requests request_id=01415578d2eb method=DELETE path=/incidents/INC-001 status=404 duration_ms=0.2 ids=INC-001
```

- **Deployed log excerpt:** TODO

## Registry and documentation

- **Class registry entry:** TODO (deployed URL + test runner location).
- **Test runner:** `tests/acceptance/` (Mohit). Run with
  `BASE_URL=<url> API_KEY=<key> uv run pytest tests/acceptance`.
- **Setup and operation docs:** `docs/setup.md`, `migrations/README.md`.
