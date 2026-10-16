# Information models and request flows

Owner: Astha; Srihari reviews architecture and storage. Feeds submission Q5.

The Phase 3 API schemas and service interfaces are implemented. See the
[feature contract and integration handoff](../incident-evidence.md) for complete
JSON fields and current limitations. The feature repository now uses Person 1's
ORM models and session dependency; PostgreSQL execution is unverified locally.

| Model | Information |
| --- | --- |
| Incident | Public ID, title, description, discovery instant, reporter, status |
| Evidence | Public ID, category, summary, source, collection instant, recording instant |
| Incident detail | Incident fields, evidence collection, null currentDecision and filing |

An incident has zero or more evidence records. Each evidence record belongs to
exactly one incident; the repository adapter must persist that association even
though the nested evidence JSON does not expose the parent ID. Public IDs use
the existing PostgreSQL computed columns (INC-001/EVD-001 and upward).

Requests flow through Pydantic validation, a thin route, `IncidentService`, and
the `IncidentRepository` interface and its SQLAlchemy adapter. PostgreSQL assigns
incident/evidence IDs and server recording times. Creation sets status to OPEN.
The adapter owns transactional persistence and maps database records back to
schema snapshots. Retrieval includes every evidence record for that incident.
No materiality or filing workflows are implemented.

Production routers are mounted and protected by shared API-key middleware;
shared handlers format errors. Non-database tests inject a test-only repository.
Conditional database tests use the real provider and require TEST_DATABASE_URL.
