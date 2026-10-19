#!/usr/bin/env bash
# Build and deploy the tester service to Google Cloud Run.
# Owner: Srihari. See docs/cross-team-testing.md.
#
# Usage:  PROJECT_ID=ece30861-project-62ca4b ALLOWED_TARGETS=https://a,https://b \
#           scripts/deploy_tester_gcp.sh [git-ref]
#
# ALLOWED_TARGETS: system base URLs this tester may target (approved pod services).
# Keys for targets come from Secret Manager: tester-target-keys (JSON
# {"<base url>": "<key>"}) if it exists, and api-key (our own system's key) as
# the default.
set -euo pipefail

: "${PROJECT_ID:?set PROJECT_ID}"
: "${ALLOWED_TARGETS:?set ALLOWED_TARGETS (comma-separated system base URLs)}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-incident-tester}"
REF="${1:-origin/integration}"

git fetch -q origin
COMMIT="$(git rev-parse --short "${REF}")"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/incident-api/tester:${COMMIT}"
echo "deploying tester from ${REF} (${COMMIT}) to ${SERVICE} in ${PROJECT_ID}"

SRC="$(mktemp -d)"
trap 'rm -rf "${SRC}"' EXIT
git archive "${REF}" | tar -x -C "${SRC}"
cat > "${SRC}/cloudbuild.yaml" <<YAML
steps:
  - name: gcr.io/cloud-builders/docker
    args: ["build", "-f", "Dockerfile.tester", "--build-arg", "GIT_COMMIT=${COMMIT}", "-t", "${IMAGE}", "."]
images: ["${IMAGE}"]
YAML
gcloud builds submit "${SRC}" --project "${PROJECT_ID}" --region "${REGION}" \
  --config "${SRC}/cloudbuild.yaml" --quiet

SECRETS="TARGET_API_KEY=api-key:latest"
if gcloud secrets describe tester-target-keys --project "${PROJECT_ID}" >/dev/null 2>&1; then
  SECRETS="${SECRETS},TARGET_API_KEYS=tester-target-keys:latest"
fi

# One instance: sessions and reports live in its memory (the spec allows that).
# --timeout 900: a run waits for the whole suite.
gcloud run deploy "${SERVICE}" --project "${PROJECT_ID}" --region "${REGION}" \
  --image "${IMAGE}" \
  --set-env-vars "^@^ALLOWED_TARGETS=${ALLOWED_TARGETS}@RUN_TIMEOUT=600@SETUP_TIMEOUT=60" \
  --set-secrets "${SECRETS}" \
  --min-instances 1 --max-instances 1 --cpu 1 --memory 1Gi --timeout 900 \
  --allow-unauthenticated --quiet

URL="$(gcloud run services describe "${SERVICE}" --project "${PROJECT_ID}" \
  --region "${REGION}" --format 'value(status.url)')"
echo "tester deployed: ${URL}"
