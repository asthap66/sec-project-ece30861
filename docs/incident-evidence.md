# Incident and evidence feature integration

## Implementation status

The schemas, service, and routers are implemented and tested in an isolated
FastAPI application with a **test-only repository**. Production `app/main.py`
remains the original scaffold. Database, authentication, and shared error
modules are still placeholders. Persistent-storage and deployed acceptance
criteria have not been verified.

## Endpoints and JSON models

Reviewed against the user-supplied **Phase 2 - Pod.docx**, pod specification
v1.0 (Q1.3), on October 16, 2026: REQ-01–03/14, Q3.2 Model 4, Q5.1–5.2,
AC-01–05, and the Q6.1 Phase 3 scope. Embedded models were also inspected.

All JSON names are camelCase. Writes are append-only; no edit/delete routes exist.

| Operation | Request | Success |
| --- | --- | --- |
| POST `/incidents` | `title`, `description`, `discoveredAt`, `reporterName` | 201: `incidentId`, `status` (`OPEN`) |
| GET `/incidents/{incidentId}` | No body | 200: incident detail below |
| POST `/incidents/{incidentId}/evidence` | `category`, `summary`, `source`, `collectedAt` | 201: `evidenceId`, `recordedAt` |

Incident detail contains `incidentId`, `title`, `description`, `discoveredAt`,
`reporterName`, `status`, `evidence`, `currentDecision`, and `filing`. The last two
are null in Phase 3. `createdAt` is not exposed. Each evidence item contains
`evidenceId`, `category`, `summary`, `source`, `collectedAt`, and `recordedAt`;
no nested `incidentId` is exposed.

Example creation request:

```json
{
  "title": "Synthetic incident",
  "description": "Synthetic description",
  "discoveredAt": "2020-01-01T10:00:00-04:00",
  "reporterName": "Test team"
}
```

Creation response (the actual generated ID varies):

```json
{"incidentId": "INC-<uuid hex>", "status": "OPEN"}
```

Example evidence request:

```json
{
  "category": "BUSINESS_IMPACT",
  "summary": "Synthetic service disruption",
  "source": "Synthetic service logs",
  "collectedAt": "2020-01-01T11:00:00-04:00"
}
```

Evidence creation returns only `evidenceId` and server-generated UTC `recordedAt`.

Required text must be a nonblank string; original whitespace is preserved.
Timestamps must include a timezone and are normalized to UTC, retaining the
instant. Discovery cannot be in the future. Evidence collection has no additional
past/future restriction. Categories: TECHNICAL, BUSINESS_IMPACT, LEGAL, OTHER.
Maximum lengths remain an open team decision. Add agreed limits to field
annotations in `app/schemas.py`; `RequiredText` centralizes common validation.

`IncidentStatus` includes OPEN, NOT_MATERIAL, MATERIAL_PENDING_FILING, and FILED.
Creation sets OPEN. Retrieval preserves stored status; no later-phase transitions
are implemented.

Feature-local `FeatureRoute` translates request-validation failures (including
malformed JSON) to 400 and `IncidentNotFoundError` to 404:

```json
{"error": "INVALID_REQUEST", "message": "Invalid request fields: discoveredAt"}
```

```json
{"error": "NOT_FOUND", "message": "Incident not found"}
```

These error codes/messages are provisional pending agreement with Person 1.
No global exception handler is installed. Model 4 specifies authentication,
endpoint/method, incident existence, body validation, then workflow-state checks.
Evidence routing explicitly checks the parent before parsing the body: unknown
parents return 404 even for malformed JSON. Errors name invalid camelCase fields;
malformed JSON reports an invalid request body. Request timestamps reject numeric
epochs and strings lacking the required timestamp structure before Pydantic
parsing. Authentication precedence, standard 405 errors, and global error
formatting remain shared infrastructure tasks. Authentication must also precede
unknown-route/method errors, requiring application-level coordination beyond
router dependencies.

## Person 1 handoff

1. Implement `IncidentRepository` from `app/services/incidents.py` using existing
   SQLAlchemy models and request-scoped sessions. `create_incident` and
   `add_evidence` must commit atomically or roll back. `get_incident` returns an
   `IncidentDetail` snapshot with all linked evidence. Evidence insertion must
   enforce the parent foreign key and raise `IncidentNotFoundError` if missing,
   including if the parent disappears after the service existence check. Enforce
   unique public IDs in the database. Store internal `created_at` in the adapter
   if required by the database; it is intentionally absent from API schemas.
2. Supply an `IncidentService` via `get_incident_service` dependency override (or
   replace that dependency with a request-scoped provider). The default raises
   503 because persistence is unconfigured; its response is an integration guard,
   not a finalized contract error.
3. No existing ID generator was present. `new_public_id` provisionally uses UUIDs
   with INC/EVD prefixes. Confirm the public format or inject the agreed generator
   through `IncidentService(id_factory=...)`; example IDs do not imply sequences.
4. Register both routers from `app.routes.incidents` and `app.routes.evidence` in
   `app/main.py`, applying `Depends(require_api_key)` to both. Do this only when
   authentication and the persistent provider are ready. Preserve public health.
5. Integrate 400/404 mapping with the shared error infrastructure, then remove the
   feature-local mapping when the global handlers provide equivalent behavior.
   Follow Model 4's authentication-first ordering and confirm final error
   codes/messages. Preserve the evidence parent-before-body check when replacing
   feature-local handling.
6. Confirm maximum text lengths and the instructor's OpenAPI contract. Verify
   real PostgreSQL persistence, rollback behavior, reset, and restart behavior.

The repository interface intentionally takes API snapshots to avoid inventing
Person 1's ORM model names or a second database architecture. A database adapter
should map these snapshots to internal models and back.

## Tests

After the normal project setup (`uv sync --locked`), run:

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

If using an already provisioned virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

`tests/unit/conftest.py` mounts the routers on an isolated app and injects a fake
repository. Its clock is fixed and its incident timestamps are historical.
Tests exercise response shapes, validation/400/404, ID uniqueness, server time,
three technical evidence records, business-impact preservation, parent isolation,
and rejected writes. They do not establish PostgreSQL or authentication coverage.

Local verification on October 16, 2026: 77 tests passed; Ruff lint and format
checks on `app`/`tests` and mypy passed. Python 3.12.5 was used. Installed
FastAPI, Pydantic, pytest, HTTPX, Starlette, Ruff, and mypy versions match
`uv.lock`. The environment reports a Starlette HTTPX deprecation warning.

## Files

- `app/schemas.py`: contract schemas and validation.
- `app/routes/incidents.py`, `app/routes/evidence.py`: feature routers.
- `app/routes/feature_support.py`: service injection and local error mapping.
- `app/services/incidents.py`: repository protocol and reusable service.
- `tests/unit/conftest.py`: isolated fixture and test repository.
- `tests/unit/test_schemas.py`, `test_incidents.py`, `test_evidence.py`: tests.
- `tests/__init__.py`, `tests/unit/__init__.py`: package markers for type checking.
- `docs/incident-evidence.md`: this handoff.
- `docs/models/README.md`: API information models and request flow.

Infrastructure files and dependency declarations are unchanged.
