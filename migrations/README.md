# Database migrations

Owner: Srihari, with model-field review from Astha.

Alembic migrations for the PostgreSQL schema. `migrations/env.py` reads
`DATABASE_URL` the same way the app does (environment, or `.env`), so there are
no credentials in `alembic.ini`.

| Revision | What it does |
| --- | --- |
| `0001` | `incidents` and `evidence` tables (Phase 3, Q5.2 fields), with database-generated public IDs (`INC-001`, `EVD-001`), timezone-aware timestamps, status/category checks, and the evidence → incident foreign key |

## Commands

```sh
uv run alembic upgrade head      # apply everything (also runs on container start)
uv run alembic check             # fails if app/models.py and the migrations disagree
uv run alembic revision -m "..."  # new migration; write upgrade/downgrade by hand and review it
```

The container applies pending migrations on every start (`scripts/start.sh`), so a
deployment always has the schema its code expects. Already-applied migrations
are skipped.

Phase 4 (decisions, corrections, filings) will add a `0002` migration; `0001` is
never edited once deployed.
