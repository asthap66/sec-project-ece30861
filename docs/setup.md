# Local setup

## Package management

The project uses [uv](https://docs.astral.sh/uv/). Dependencies are declared in `pyproject.toml`: runtime dependencies under `[project]`, development tools under `[dependency-groups].dev`. Exact resolved versions are pinned in `uv.lock`, which is committed. CI installs with `uv sync --locked`, so it fails if the lock is out of date.

To add a dependency, run `uv add <pkg>` (or `uv add --dev <pkg>`) and commit both `pyproject.toml` and `uv.lock`. Srihari coordinates dependency changes.

## Environment setup

Prerequisites: Python 3.12, uv, and Docker (only needed for PostgreSQL and the container).

```sh
cp .env.example .env   # local placeholders only; .env is git-ignored
```

## Install dependencies

```sh
uv sync                # creates .venv with Python 3.12, plus runtime and dev dependencies
```

## Run the app

```sh
uv run uvicorn app.main:app --reload
```

The app registers health, reset, incident creation/retrieval, and evidence
attachment endpoints. Configure DATABASE_URL/API_KEY and apply migrations before
using the persistent endpoints. See [feature integration](incident-evidence.md).

## Start local PostgreSQL

```sh
docker compose up -d db        # PostgreSQL only
uv run alembic upgrade head    # create/upgrade the tables
docker compose up --build      # app + PostgreSQL; the app applies migrations, then starts
docker compose down            # stop containers; keeps data
```

If you already run PostgreSQL on your machine, port 5432 is taken and you'll
reach that server instead of the container. Set `POSTGRES_PORT=5433` in `.env`
and use port 5433 (host `127.0.0.1`) in `DATABASE_URL`.

Database data lives in the named volume `pgdata` and survives `docker compose down`. **`docker compose down -v` (or `docker volume rm`) deletes the volume and all local database data.**

## Tests and static checks

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

Tests that need a database (`tests/infrastructure/test_database.py` and
`tests/infrastructure/test_feature_database.py`) are
skipped unless `TEST_DATABASE_URL` points at a **disposable** PostgreSQL: they
reset it. For example, against the local container:

```sh
TEST_DATABASE_URL=postgresql+psycopg://incident_app:change-me-local-only@127.0.0.1:5432/incident_db uv run pytest tests/infrastructure
```

Acceptance tests run against a running service:

```sh
BASE_URL=http://localhost:8000 API_KEY=replace-with-local-dev-key uv run pytest tests/acceptance
```

CI (`.github/workflows/ci.yml`) runs on pushes to `main` and `integration`, and on pull requests. It does three things:

- Runs the static checks.
- Runs the non-acceptance tests against a disposable PostgreSQL service (`TEST_DATABASE_URL`), so the database tests run instead of skipping.
- Migrates and starts the app locally, then runs `pytest -m acceptance` against it with a throwaway key.

Runs against a deployed service are done separately and are never triggered from CI.

## Current limitations

- Implemented: `GET /health` (public), `POST /reset`, API-key authentication on every other path, the contract's error format, request logging, the Incident/Evidence models and first migration.
- Incident/evidence routes now use the shared models, session, auth, and error
  infrastructure. Local PostgreSQL verification and deployment over HTTPS remain
  unverified; see `docs/incident-evidence.md` for the test scope.
- Field length limits for `title`/`description` are placeholders in `app/config.py` until the pod agrees on numbers (`docs/contract-issues.md` #3).

## Configuration

- Server: `DATABASE_URL`, `API_KEY` (read on first use, so importing the app doesn't need them). `PORT` sets the listening port in the container (default 8000).
- Acceptance runner: `BASE_URL`, `API_KEY` (the target service and its key).
- Local tests: `TEST_DATABASE_URL` (a disposable database; see above).
