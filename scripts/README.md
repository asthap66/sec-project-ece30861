# Scripts

Owner: Mohit.

Planned (none exist yet):

- `performance.py`: load 100 synthetic incidents, time 200 requests, and report the share completed in under one second along with the test conditions.
- `check_persistence.py`: create data, restart the app without a reset, and confirm the same data can be retrieved. This may end up as a documented manual procedure instead.

Both scripts will read `BASE_URL` and `API_KEY` from the environment. Never hardcode deployed URLs or credentials.
