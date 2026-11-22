# Test fixtures

Owner: Mohit.

Synthetic data for the acceptance tests. The JSON files in `data/` are plain JSON, so we can share them with the other team (Phase 2, Q4.2) without them needing our code:

| File | Contents |
| --- | --- |
| `data/incidents_valid.json` | Valid `POST /incidents` bodies (AC-01), each with the expected `status` and the UTC-normalized `discoveredAt` |
| `data/incidents_invalid.json` | Bodies that must be rejected with 400 naming `expected.field`. Includes AC-02's three cases |
| `data/evidence_valid.json` | One evidence item per category, including AC-04's three TECHNICAL items and AC-05's BUSINESS_IMPACT item |
| `data/evidence_invalid.json` | Evidence bodies that must be rejected with 400 |
| `data/unknown_ids.json` | Incident IDs the tests never create (AC-03) |
| `data/phase5_scenarios.json` | Independent decision, correction, filing-boundary, invalid-case, timeline-order, restart and reset scenarios. These are scenario oracles, not approved HTTP request/response schemas. |

Each case has the shape `{"name", "body", "expected"}`. `data.py` loads the files, and `test_fixture_data.py` checks them against the contract's field rules in CI.

Not included yet: maximum-length boundary cases. They're waiting on the agreed limits (`docs/contract-issues.md` #3).

Use synthetic data only. No real incident data and no credentials.

`test_phase5_data.py` checks chronology, Eastern filing-date classifications,
independent business-days-late examples,
scenario completeness, and event order without importing production code. It
does not claim Phase 5 API conformance. `test_phase5_workflow.py` uses the
public shapes in Astha's Phase 5 handoff and these fixed inputs; its live HTTP
checks require Srihari's adapter before they can pass.
