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

The scaffold serves only FastAPI's generated docs (`/docs`, `/openapi.json`). It has no business endpoints yet.

## Start local PostgreSQL

```sh
docker compose up -d db        # PostgreSQL only
docker compose up --build      # app + PostgreSQL; the app waits for the DB health check
docker compose down            # stop containers; keeps data
```

Database data lives in the named volume `pgdata` and survives `docker compose down`. **`docker compose down -v` (or `docker volume rm`) deletes the volume and all local database data.**

## Tests and static checks

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

### Acceptance tests (live service)

Tests marked `acceptance` (in `tests/acceptance/`) run against a live service and skip when `BASE_URL` is unset. That is why CI reports them as skipped.

```sh
BASE_URL=http://localhost:8000 API_KEY=<key> uv run pytest -m acceptance
```

Tests that call `POST /reset` also require `ALLOW_DESTRUCTIVE_TESTS=1`. Only set that against the agreed synthetic test service, and serialize runs with the other team.

CI (`.github/workflows/ci.yml`) runs the same commands on pushes to `main` and on pull requests.

## Current scaffold limitations

- No business endpoints. `/health`, `/reset`, `/incidents`, and evidence routes do not exist yet.
- No authentication, database models, migrations, or DB connection code. The app does not connect to PostgreSQL yet.
- No deployment.
- Tests that run in CI: the scaffold smoke test and the acceptance-client self-tests. Neither is acceptance coverage.
- The instructor-provided OpenAPI contract hasn't been added. See `docs/contract-issues.md`.

## Configuration variables (planned, not implemented)

- `DATABASE_URL`, `API_KEY`: planned **server** configuration. The scaffold doesn't read them, and the app imports without them.
- `BASE_URL`, `API_KEY`: **acceptance-runner** configuration (the target service and its key), read by `tests/acceptance/client.py`. The server-side behavior these tests check isn't implemented yet.
- `ALLOW_DESTRUCTIVE_TESTS=1`: opt-in for acceptance tests that reset the target's data.
