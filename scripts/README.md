# Scripts

Both scripts read `BASE_URL` and `API_KEY` from the environment. Never hardcode deployed URLs or credentials. Anything that calls `POST /reset` also requires `ALLOW_DESTRUCTIVE_TESTS=1`. Only point those at the agreed synthetic test service, and agree a time with the other team first.

| Script | Owner | Purpose |
| --- | --- | --- |
| `start.sh` | Srihari | Container entry point: migrate, then serve |
| `performance.py` | Mohit | AC-16 response time: loads 100 incidents, times 200 sequential requests, passes if at least 95% finish within 1 s. Prints the test conditions with the result |
| `check_persistence.py` | Mohit | AC-16 restart persistence and reset, in three steps: `create`, restart the service yourself, `verify`, then (destructive) `reset` |
| `common.py` | Mohit | Shared client, fixture loading and run conditions |

```sh
export BASE_URL=https://<deployment> API_KEY=<shared test key>

uv run python -m scripts.check_persistence create --state run.json
# restart the service WITHOUT /reset (locally: docker compose restart app)
uv run python -m scripts.check_persistence verify --state run.json

uv run python -m scripts.performance --json-out perf.json

ALLOW_DESTRUCTIVE_TESTS=1 uv run python -m scripts.check_persistence reset --state run.json
```

Exit codes: 0 means pass, 1 means fail, 2 means the script couldn't run (bad configuration, or setup requests failed). Record each real run in `docs/test-results/`.
