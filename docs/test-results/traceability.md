# Requirement / test traceability

Owner: Mohit. Feeds submission Q4. Status reflects code in the repo, not deployed results. Record actual runs in this folder.

| Criterion | Planned coverage (README §5) | Tests | Status |
| --- | --- | --- | --- |
| AC-01 – AC-04 | Incident create/retrieve workflow, including success, failure, and boundary cases | Fixtures: `tests/fixtures/data/incidents_*.json`, `evidence_valid.json` and `test_ac01_05_incidents_evidence.py` | Written. All pass against integration merged with Astha's PR #4, run locally. Length boundaries wait on issue #3. AC-02's count check waits on issue #2 |
| AC-02 | Includes listing incidents | — | Blocked: `GET /incidents` existence (issue #2) |
| AC-03 (GET half) | Unknown incident ID returns 404 with error code and message | `test_system_endpoints.py::test_unknown_incident_get_is_404_with_error_format` | GET half passes against the app run locally and in CI. POST half is in `test_ac01_05_incidents_evidence.py` |
| AC-05 | Evidence attachment, where the increment supports it | Fixtures: `tests/fixtures/data/evidence_*.json` and `test_ac01_05_incidents_evidence.py` | Written. All pass against integration merged with Astha's PR #4, run locally |
| AC-14 | Public health endpoint | `test_ac14_security.py::test_health_is_public` | Passes against the app run locally and in CI; not yet run against a deployment |
| AC-14 | Missing / wrong / valid API key | `test_ac14_security.py::test_authenticated_route_*` | Passes against the app run locally and in CI; assumes auth before 404 (issue #4) |
| AC-14 | HTTPS deployment | `test_ac14_security.py::test_deployment_uses_https` | Written; skips for local targets |
| AC-16 | Reset | `test_system_endpoints.py::test_reset_*` (destructive, opt-in); `scripts.check_persistence reset` (each created ID returns 404 afterwards); Srihari's `tests/infrastructure/test_database.py` | Passes locally ([2026-10-16 run](2026-10-16-local-ac16.md)) and in CI. "No incidents remain" is checked per ID until issue #2 is settled |
| AC-14 | Errors use `{error, message}` | `test_system_endpoints.py::test_401_uses_error_format` | Passes against the app run locally and in CI |
| AC-16 | Restart persistence | `scripts.check_persistence create` / restart / `verify` | 100/100 intact after an app restart and after a full stack restart, run locally ([2026-10-16](2026-10-16-local-ac16.md)). In CI after an app restart. Deployment run pending |
| AC-16 | Response time (100 incidents, 200 requests) | `scripts.performance` | 100% within 1 s, run locally ([2026-10-16](2026-10-16-local-ac16.md)). Smoke run in CI. Deployment run pending |

Before any service existed, the AC-14 tests were checked two ways. Against a throwaway local stub with `/health` and key checking, they passed (HTTPS check skipped). Against the current scaffold, which has no routes, they failed as expected. Neither run is a result for the real service.
