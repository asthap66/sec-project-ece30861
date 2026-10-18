# Q2 Deployment and operation (draft)

Lead: Srihari. Everything below was observed on 2026-10-18 unless noted.
Operating details: `docs/deployment.md`.

## Host and runtime

- **Host:** Google Cloud Run (managed containers), project
  `ece30861-project-62ca4b`, region `us-central1`.
- **Runtime:** one Docker image (`Dockerfile`): Python 3.12, FastAPI served by
  Uvicorn, dependencies installed from the locked `uv.lock`, running as a
  non-root user. 1 vCPU, 512 MiB, min 1 / max 2 instances. One instance is kept
  warm so no request waits for a cold start (REQ-15).
- **Database:** Cloud SQL for PostgreSQL 16 (`db-f1-micro`, 10 GB SSD),
  connected through Cloud Run's built-in Cloud SQL connector. It is separate
  from the app, so app restarts and redeploys don't touch the data.
- **HTTPS:** provided by Cloud Run with a Google-managed certificate. Plain
  `http://` gets a 302 redirect to `https://`. AC-14's HTTPS check passes
  against the deployment.

## Deployed URL

- **Base URL:** https://incident-api-356019173418.us-central1.run.app
- **Public endpoint:** `GET /health` → `200 {"status": "OK"}` (75 ms when checked).
- Every other endpoint needs the shared test key in `X-API-Key`.

## Commit mapping

Every response carries an `X-App-Commit` header with the git commit the
running image was built from. Images are built from a clean `git archive` of
the ref, tagged with the commit (`.../incident-api/api:<commit>`), and deployed
with `scripts/deploy_gcp.sh`.

```sh
curl -sI https://incident-api-356019173418.us-central1.run.app/health | grep -i x-app-commit
```

- **Deployed commit:** `f2b607c` (`integration` branch: infra + incident/evidence
  API + acceptance tests). Checked with the header above.

## Secrets

- `DATABASE_URL` and `API_KEY` are stored in Google Secret Manager and given
  to the service as environment variables at start. They are not in git,
  images, logs or this report. `.env` is git-ignored; `.env.example` has
  placeholders only. The database password and API key were randomly generated.
- The API key is compared in constant time; a blank configured key rejects every
  request instead of disabling authentication.
- **Sharing the test key:** project members read it with
  `gcloud secrets versions access latest --secret api-key`. It is shared with
  teammates and the other team over a private channel only.

## Persistence, startup and restart

- On start the container applies pending migrations (`alembic upgrade head`),
  then serves (`scripts/start.sh`). Already-applied migrations are skipped.
- Data stays until `POST /reset`, which clears evidence and incidents in one
  transaction and restarts the IDs at `INC-001`.
- **Restart procedure:** roll out a new revision of the same image
  (`gcloud run services update incident-api ... --update-env-vars RESTARTED_AT=<time>`),
  which replaces the running instances. See `docs/deployment.md`.
- **Restart check (deployed):** `scripts/check_persistence.py` created 100
  incidents, the service was restarted (revision `incident-api-00002-msv` →
  `incident-api-00003-ggj`) without a reset, and `verify` found **100/100
  incidents intact**. `reset` then removed all 100.
- Local check (2026-10-16): the same behaviour with `docker compose restart app`.

## Validation against the deployment (2026-10-18)

| Check | Result |
| --- | --- |
| Acceptance suite (`pytest -m acceptance`, AC-01 to AC-05, AC-14) | **48 passed**, 0 failed, 0 skipped |
| Restart persistence (AC-16) | 100/100 incidents intact after restart; 0 after reset |
| Performance (AC-16): 100 incidents loaded, 200 sequential requests from a laptop | **200/200 within 1 s** (needs 95%); p50 48 ms, p95 61 ms, max 76 ms; 0 errors |

One unexplained event: on the first persistence run, one request timed out on
the client side (10 s), so that run was repeated. Cloud Run's request logs for
that period show no request slower than 0.36 s, so the delay was most likely on
the network path between the laptop and Google, not in the service. It did not
recur.

## Logging

One line per request: request ID, method, path, status, duration, and any
record IDs in the path. Headers (which carry the API key) and request/response
bodies (which carry incident details) are never logged. The request ID is also
returned in `X-Request-Id`, so a client-side failure can be matched to its log
line. Logs go to Google Cloud Logging.

Sanitized excerpt from the **deployed** service (2026-10-18, commit `f2b607c`):
health check, `/reset` without and with the key, create an incident, add
evidence, get it, and a delete attempt (405).

```
2026-10-18 19:40:22,869 INFO app.requests request_id=ba4ccca74e1d method=GET path=/health status=200 duration_ms=51.6 ids=-
2026-10-18 19:40:23,177 INFO app.requests request_id=be1d4edd1d95 method=POST path=/reset status=401 duration_ms=0.5 ids=-
2026-10-18 19:40:23,608 INFO app.requests request_id=0785fb07db62 method=POST path=/reset status=200 duration_ms=340.3 ids=-
2026-10-18 19:40:23,736 INFO app.requests request_id=e99251818bbb method=POST path=/incidents status=201 duration_ms=28.5 ids=-
2026-10-18 19:40:23,858 INFO app.requests request_id=1064e8509aa6 method=POST path=/incidents/INC-001/evidence status=201 duration_ms=28.2 ids=INC-001
2026-10-18 19:40:23,965 INFO app.requests request_id=382ff3c35fc9 method=GET path=/incidents/INC-001 status=200 duration_ms=12.9 ids=INC-001
2026-10-18 19:40:24,094 INFO app.requests request_id=7a4f9e667048 method=DELETE path=/incidents/INC-001 status=405 duration_ms=0.7 ids=INC-001
```

## Registry and documentation

- **Class registry entry:** TODO (submit the base URL above and the test-runner
  location below).
- **Test runner:** `tests/acceptance/` (Mohit). Run with
  `BASE_URL=<url> API_KEY=<key> uv run pytest -m acceptance`.
- **Docs:** `docs/deployment.md` (operating the deployment), `docs/setup.md`
  (local setup), `migrations/README.md`.

## Cost

About $20–25/month (Cloud SQL plus one warm instance), on the project's own
free-trial billing; a $50 budget sends alerts at 50%, 100% and forecast 100%.
