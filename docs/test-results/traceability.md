# Requirement / test traceability

Owner: Mohit. Feeds submission Q4. Status reflects code in the repo, not deployed results. Record actual runs in this folder.

| Criterion | Planned coverage (README §5) | Tests | Status |
| --- | --- | --- | --- |
| AC-01 – AC-04 | Incident create/retrieve workflow, including success, failure, and boundary cases | — | Blocked on contract (issues #1, #3) |
| AC-02 | Includes listing incidents | — | Blocked: `GET /incidents` existence (issue #2) |
| AC-05 | Evidence attachment, where the increment supports it | — | Blocked on contract (issues #1, #3) |
| AC-14 | Public health endpoint | `test_ac14_security.py::test_health_is_public` | Written; not yet run against a real service |
| AC-14 | Missing / wrong / valid API key | `test_ac14_security.py::test_authenticated_route_*` | Written; assumes auth before 404 (issue #4) |
| AC-14 | HTTPS deployment | `test_ac14_security.py::test_deployment_uses_https` | Written; skips for local targets |
| AC-16 | Reset | `reset_service` fixture (opt-in) | Fixture only; no tests yet |
| AC-16 | Restart persistence | — | Not started; coordinate with Srihari |
| AC-16 | Response time (100 incidents, 200 requests) | — | Not started; needs a create payload |

Before any service existed, the AC-14 tests were checked two ways. Against a throwaway local stub with `/health` and key checking, they passed (HTTPS check skipped). Against the current scaffold, which has no routes, they failed as expected. Neither run is a result for the real service.
