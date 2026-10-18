#!/usr/bin/env bash
# Build and deploy the API to Google Cloud Run.
# Owner: Srihari (infrastructure). See docs/deployment.md for the one-time
# setup (project, Cloud SQL, secrets) this assumes is already done.
#
# Usage:  PROJECT_ID=ece30861-project-62ca4b scripts/deploy_gcp.sh [git-ref]
#
# Builds the image from a clean `git archive` of the ref (default:
# origin/integration), so local files like .env can never end up in it, and
# tags it with the commit, which the running service reports in X-App-Commit.
set -euo pipefail

: "${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-incident-api}"
SQL_INSTANCE="${SQL_INSTANCE:-incident-db}"
REF="${1:-origin/integration}"

git fetch -q origin
COMMIT="$(git rev-parse --short "${REF}")"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/incident-api/api:${COMMIT}"
echo "deploying ${REF} (${COMMIT}) to ${SERVICE} in ${PROJECT_ID}"

SRC="$(mktemp -d)"
trap 'rm -rf "${SRC}"' EXIT
git archive "${REF}" | tar -x -C "${SRC}"
cat > "${SRC}/cloudbuild.yaml" <<YAML
steps:
  - name: gcr.io/cloud-builders/docker
    args: ["build", "--build-arg", "GIT_COMMIT=${COMMIT}", "-t", "${IMAGE}", "."]
images: ["${IMAGE}"]
YAML
gcloud builds submit "${SRC}" --project "${PROJECT_ID}" --region "${REGION}" \
  --config "${SRC}/cloudbuild.yaml" --quiet

# min-instances 1 keeps one instance warm so no request pays a cold start
# (REQ-15: 95% of requests within 1 s). Secrets come from Secret Manager.
gcloud run deploy "${SERVICE}" --project "${PROJECT_ID}" --region "${REGION}" \
  --image "${IMAGE}" \
  --add-cloudsql-instances "${PROJECT_ID}:${REGION}:${SQL_INSTANCE}" \
  --set-secrets "DATABASE_URL=database-url:latest,API_KEY=api-key:latest" \
  --min-instances 1 --max-instances 2 --cpu 1 --memory 512Mi \
  --allow-unauthenticated --quiet

URL="$(gcloud run services describe "${SERVICE}" --project "${PROJECT_ID}" \
  --region "${REGION}" --format 'value(status.url)')"
echo "deployed: ${URL}"
echo "check:    curl -sI ${URL}/health | grep -i x-app-commit   (expect ${COMMIT})"
