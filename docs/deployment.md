# Deployment (Google Cloud Run)

Owner: Srihari (infrastructure).

| | |
| --- | --- |
| Base URL | https://incident-api-356019173418.us-central1.run.app |
| Project | `ece30861-project-62ca4b` (Google Cloud, its own billing account; $50 budget alert) |
| Region | `us-central1` |
| App | Cloud Run service `incident-api`: 1 vCPU, 512 MiB, min 1 / max 1 instances (test sessions need a single instance) |
| Database | Cloud SQL `incident-db`: PostgreSQL 16, `db-f1-micro`, 10 GB SSD, database `incident_db`, user `incident_app` |
| Secrets | Secret Manager: `api-key` (the shared X-API-Key), `database-url` |
| Tester | Cloud Run service `incident-tester`: https://incident-tester-356019173418.us-central1.run.app, deployed with `scripts/deploy_tester_gcp.sh`; see `docs/cross-team-testing.md` |
| Images | Artifact Registry `us-central1-docker.pkg.dev/ece30861-project-62ca4b/incident-api/api:<commit>` |

HTTPS is provided by Cloud Run; plain `http://` redirects to `https://`. One
instance is always kept warm so no request waits for a cold start (REQ-15).

## Deploy

```sh
PROJECT_ID=ece30861-project-62ca4b scripts/deploy_gcp.sh            # deploys origin/integration
PROJECT_ID=ece30861-project-62ca4b scripts/deploy_gcp.sh origin/main
```

The image is built in Cloud Build from a clean `git archive` of the ref, so local
files (like `.env`) never end up in it, and is tagged with the commit. On start
the container applies pending migrations, then serves (`scripts/start.sh`).

Check what is running:

```sh
curl -sI https://incident-api-356019173418.us-central1.run.app/health | grep -i x-app-commit
```

## Restart (without losing data)

Data lives in Cloud SQL, so restarting the app never touches it. To restart,
roll out a new revision of the same image:

```sh
gcloud run services update incident-api --project ece30861-project-62ca4b \
  --region us-central1 --update-env-vars "RESTARTED_AT=$(date -u +%Y%m%dT%H%M%SZ)"
```

This replaces the running instances. Only `POST /reset` deletes data.

## Logs

```sh
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="incident-api" AND textPayload:"app.requests"' \
  --project ece30861-project-62ca4b --freshness 1h --limit 50 --format 'value(textPayload)'
```

Request logs never contain the API key or request/response bodies.

## The API key

The shared test key is in Secret Manager (`api-key`); it is **not** in this repo.
To read it (project members only):

```sh
gcloud secrets versions access latest --secret api-key --project ece30861-project-62ca4b
```

Share it with teammates and the other team over a private channel, never in the
repo, issues, screenshots or the report. To rotate it, add a new version and
redeploy:

```sh
openssl rand -base64 36 | tr -d '/+=\n' | gcloud secrets versions add api-key \
  --project ece30861-project-62ca4b --data-file=-
PROJECT_ID=ece30861-project-62ca4b scripts/deploy_gcp.sh
```

## One-time setup (already done, 2026-10-18)

For reference, in case it ever has to be rebuilt:

1. Project with its own billing; enable `run`, `sqladmin`, `secretmanager`,
   `artifactregistry`, `cloudbuild`.
2. `gcloud sql instances create incident-db --database-version POSTGRES_16 --edition ENTERPRISE --tier db-f1-micro --region us-central1 ...`,
   then `gcloud sql databases create incident_db` and `gcloud sql users create incident_app`.
3. Secrets `api-key` and `database-url`
   (`postgresql+psycopg://incident_app:<password>@/incident_db?host=/cloudsql/<project>:us-central1:incident-db`).
4. Grant the Cloud Run runtime service account
   `roles/secretmanager.secretAccessor` and `roles/cloudsql.client`.
5. Artifact Registry repository `incident-api`, then `scripts/deploy_gcp.sh`.

If you script any of this in zsh, write `${PROJECT_ID}:us-central1`, not
`$PROJECT_ID:us-central1`: zsh reads `:u` as "uppercase" and mangles the name.
That happened during setup and briefly broke the database URL secret.

## Cost

Roughly $20–25/month (Cloud SQL `db-f1-micro` plus one warm Cloud Run
instance), covered by the free-trial credit. A $50 budget on the project emails
at 50%, 100% and forecast 100%. To stop all charges at the end of the course,
delete the project.
