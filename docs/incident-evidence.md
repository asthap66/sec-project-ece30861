# Incident and evidence integration

## Current implementation

The production FastAPI app registers POST `/incidents`, GET
`/incidents/{incidentId}`, and POST `/incidents/{incidentId}/evidence`.
`get_incident_service` wraps Person 1's `get_db` session in
`SQLAlchemyIncidentRepository`. There is no second engine, session factory,
authentication system, or production in-memory store.

Reviewed against user-supplied Phase 2 - Pod.docx, pod spec v1.0: REQ-01–03/14,
Q3.2 Model 4, Q5.1–5.2, AC-01–05, and Q6.1. Phase 4/5 operations are absent.

## API contract

All JSON names are camelCase. Required text rejects blanks and preserves the
submitted text. Request timestamps use RFC 3339 with an offset; responses use UTC.
Discovery cannot be in the future. Evidence collection has no extra time-order
or future-date restriction. Categories: TECHNICAL, BUSINESS_IMPACT, LEGAL, OTHER.

| Operation | Request fields | Success |
| --- | --- | --- |
| POST `/incidents` | title, description, discoveredAt, reporterName | 201: incidentId, status (`OPEN`) |
| GET `/incidents/{incidentId}` | No body | 200: incident detail below |
| POST `/incidents/{incidentId}/evidence` | category, summary, source, collectedAt | 201: evidenceId, recordedAt |

Incident detail contains incidentId, title, description, discoveredAt,
reporterName, status, evidence, currentDecision, and filing. The last two are null
in Phase 3. Each evidence object contains evidenceId, category, summary, source,
collectedAt, and recordedAt. Internal createdAt and nested incidentId are absent.

Example incident request:

```json
{
  "title": "Synthetic incident",
  "description": "Synthetic report",
  "discoveredAt": "2020-01-01T10:00:00-04:00",
  "reporterName": "Test team"
}
```

Example creation response:

```json
{"incidentId": "INC-001", "status": "OPEN"}
```

Example evidence request:

```json
{
  "category": "BUSINESS_IMPACT",
  "summary": "Synthetic impact",
  "source": "Synthetic logs",
  "collectedAt": "2020-01-01T11:00:00-04:00"
}
```

Evidence creation returns only evidenceId and recordedAt. PostgreSQL generates
public IDs using the existing computed columns (`INC-001`, `EVD-001`, increasing
without truncation after 999) and sets created_at/recorded_at using its server
clock. The client cannot set these through the request schemas.

## Persistence and errors

Each request uses the shared session dependency. The adapter flushes to fetch
server-generated values, builds the response snapshot, and commits once. It
rolls back on failure. Evidence uses the existing incident foreign key and locks
the parent until insertion commits to protect against concurrent reset/deletion.
Retrieval eagerly loads linked evidence in internal ID order.

The existing `ApiKeyMiddleware` protects the feature routes before routing or
body validation. The feature introduces no additional public paths. Health and
the shared middleware's existing generated-documentation exemptions are unchanged.

`IncidentNotFoundError` subclasses shared `ApiError` (404/NOT_FOUND). Validation
raises FastAPI's `RequestValidationError`, mapped by shared handlers to 400 with
a field-specific code/message, for example:

```json
{"error": "INVALID_DESCRIPTION", "message": "description is required"}
```

The previous feature-local error handlers and unconfigured-service 503 guard
have been removed. Shared handlers also format 401 and 405 errors. Evidence
checks the parent before parsing its body, so unknown parents return 404 even
for malformed JSON, following Model 4. No edit/delete routes exist. Evidence may
be attached in any stored status; these operations never change incident status.

## Configuration and unresolved decisions

- Server requires DATABASE_URL and API_KEY. Apply the existing migration with
  `uv run alembic upgrade head` before serving requests.
- TEST_DATABASE_URL must point to a disposable PostgreSQL database: database
  fixtures migrate it and clear all incident/evidence data. BASE_URL and API_KEY
  are needed for live acceptance tests.
- Shared config and the existing migration currently constrain title to 200,
  description to 5000, reporterName/source to 500 characters. Request validation
  now uses these same constants to return 400 instead of a database truncation
  error. These are existing provisional storage limits, **not pod-approved
  contract decisions**. Final limits require agreement and coordinated
  schema/config/migration updates. Summary remains unrestricted nonblank text.
- Instructor OpenAPI is absent; the GET collection route discrepancy and exact
  error-code naming still need pod confirmation. See `contract-issues.md`.

## Verification and how to run

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m ruff format --check app tests
.\.venv\Scripts\python.exe -m mypy
```

For PostgreSQL-backed tests, provision a dedicated throwaway PostgreSQL service,
set TEST_DATABASE_URL to its SQLAlchemy URL, then run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/infrastructure/test_database.py tests/infrastructure/test_feature_database.py
```

The existing CI service already supplies TEST_DATABASE_URL, so these tests are
included in its non-acceptance pytest run without changing CI.

Verification scope:

- `tests/unit`: schemas, service interface, and mocked-session rollback behavior;
  test-only repository, not PostgreSQL.
- `tests/infrastructure/test_feature_routes.py`: real app registration, shared
  authentication and errors, request precedence, append-only routes; injects a
  test-only repository, not PostgreSQL.
- `tests/infrastructure/test_feature_database.py`: real provider, PostgreSQL
  generated IDs/timestamps, create/retrieve, multiple evidence records and
  business impact, parent isolation, rejected writes, reset, and a new app/pool
  persistence check. Skips without TEST_DATABASE_URL. A new app/pool does not
  establish persistence through an actual process/container restart.

Local environment has no TEST_DATABASE_URL, Docker/PostgreSQL command, or
PostgreSQL listener on 5432. **No tests exercised PostgreSQL locally.** Live
acceptance/deployment, HTTPS, actual restart persistence, and performance remain
unverified. The environment emits a Starlette HTTPX deprecation warning.

Final local run on October 16, 2026: **117 passed, 16 skipped, 0 failed**.
Eleven skipped tests require PostgreSQL; five require a running acceptance
service. Ruff lint/format checks and mypy passed. Changes remain uncommitted
on `feature/incident-evidence-api`.

## Modified files

- app/main.py: register feature routers.
- app/routes/incidents.py and evidence.py: use shared handlers via plain routers.
- app/routes/feature_support.py: shared-session service provider.
- app/services/incidents.py: SQLAlchemy repository and shared domain error.
- app/schemas.py: reuse current storage limits.
- tests/unit/conftest.py: update the fake repository interface and shared handlers.
- tests/unit/test_schemas.py and test_repository.py: boundaries and rollback.
- tests/infrastructure/test_auth.py and test_errors.py: keep non-database tests
  independent of the newly mounted database routes.
- tests/infrastructure/test_feature_routes.py and test_feature_database.py:
  app integration and conditional PostgreSQL workflow coverage.
- docs/incident-evidence.md, docs/models/README.md, docs/setup.md, and
  docs/contract-issues.md: current integration and verification status.
