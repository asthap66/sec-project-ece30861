# Phase 5 integration and cross-team evidence

This is a procedure, not a result. Srihari supplies the final API and tester
revisions/URLs and confirms the migration and deployed version. Astha supplies
the final route/schema handoff. Mohit compares it to the shared contract,
completes route tests, and requests an exclusive reset window with the other
team before running either tester against a shared service.

For each direction, record: UTC start/end, target API URL and `X-App-Commit`,
tester URL and commit/revision, reset owner/window, command or tester session
ID, pass/fail/error/skip counts, JUnit and JSONL paths, coverage basis, each
failure's expected/actual response and owner, fixes, and rerun ID. Save reports
under `docs/test-results/` only after a real run. Run our tester on their API
and their tester on ours in separate windows. Do not publish keys or private
database URLs.

For local Phase 5 persistence evidence, use a disposable PostgreSQL database:
create an incident, evidence, original decision, correction and filing; save
the returned IDs and complete timeline. Stop the app without resetting or
destroying the database, restart the same revision, and compare the retrieved
data. Then use the agreed synthetic reset and verify the known IDs are absent
while a separately seeded unrelated record remains. The current reset endpoint
deletes all records, so this isolation check requires Srihari's Phase 5 reset
design; it cannot be performed against the current API without losing the
unrelated record.

No Phase 5 deployment, reciprocal run, or reset window has been provided as of
this branch. These outcomes remain pending.
