"""FastAPI application entry point.

Owner: Srihari (infrastructure).

Scaffold only: no routers are registered yet. Register routers from
``app.routes`` here as each one is implemented against the agreed contract.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Cybersecurity Incident and Evidence Management API",
    version="0.1.0",
)
