# Database migrations (planned)

Owner: Srihari, with model-field review from Astha.

No migrations exist yet, deliberately. An empty migration would suggest a schema has been implemented when it hasn't.

## Planned Alembic setup

1. After `app/models.py` defines the Incident and Evidence models, run `uv run alembic init migrations` (move this README aside first, or merge it into the generated files).
2. Configure `env.py` to read `DATABASE_URL` from application config and to use the models' `Base.metadata` as `target_metadata`.
3. Generate the initial revision with `uv run alembic revision --autogenerate -m "create incidents and evidence"`, then review it by hand: foreign keys, timezone-aware timestamp columns, and agreed length limits.
4. Apply with `uv run alembic upgrade head`, against the local Compose database first.
5. Once real migrations exist, add a CI step that runs them against a disposable PostgreSQL service.
