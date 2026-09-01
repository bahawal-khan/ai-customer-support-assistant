#!/bin/sh
# Production container entrypoint (docs/deployment/DEPLOYMENT_SPEC.md: "database
# migrations run successfully" then "backend starts"). Runs from /app/backend so
# relative alembic/app imports resolve exactly as they do in local development.
set -e

cd "$(dirname "$0")"

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
