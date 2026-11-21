#!/bin/sh
# Start the API: apply database migrations, then serve.
# Owner: Srihari (infrastructure).
# Migrations are idempotent (already-applied ones are skipped), so this is safe
# on every restart and keeps the deployed database in step with the code.
set -e
alembic upgrade head
# Most hosts set $PORT; default to 8000 locally. --proxy-headers so the app sees
# the original https scheme when it sits behind the host's TLS proxy.
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips='*'
