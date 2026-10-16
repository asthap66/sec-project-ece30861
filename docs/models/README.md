# Information models and request flows

Owner: Astha; Srihari reviews architecture and storage. Feeds submission Q5.

The Phase 3 API schemas and service interfaces are implemented. See the
[feature contract and integration handoff](../incident-evidence.md) for complete
JSON fields and current limitations. ORM models and database integration remain
Person 1's work; these are API information models, not deployed storage models.

| Model | Information |
| --- | --- |
| Incident | Public ID, title, description, discovery instant, reporter, status |
| Evidence | Public ID, category, summary, source, collection instant, recording instant |
| Incident detail | Incident fields, evidence collection, null currentDecision and filing |

An incident has zero or more evidence records. Each evidence record belongs to
exactly one incident; the repository adapter must persist that association even
though the nested evidence JSON does not expose the parent ID. Public IDs are
provisionally UUID based pending the team's format decision.

Requests flow through Pydantic validation, a thin route, `IncidentService`, and
the `IncidentRepository` interface. The service assigns incident/evidence IDs,
initializes incident status to OPEN, and records server UTC time for evidence.
The adapter owns transactional persistence and maps database records back to
schema snapshots. Retrieval includes every evidence record for that incident.
No materiality or filing workflows are implemented.

Tests inject a test-only repository into an isolated FastAPI application.
Production routers are not yet mounted because persistence and authentication
dependencies are not implemented.
