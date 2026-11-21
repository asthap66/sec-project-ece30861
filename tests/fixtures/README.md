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

Each case has the shape `{"name", "body", "expected"}`. `data.py` loads the files, and `test_fixture_data.py` checks them against the contract's field rules in CI.

Not included yet: maximum-length boundary cases. They're waiting on the agreed limits (`docs/contract-issues.md` #3).

Use synthetic data only. No real incident data and no credentials.
