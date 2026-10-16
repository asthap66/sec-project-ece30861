"""PostgreSQL engine/session lifecycle and the get_db() dependency.

Owner: Srihari (infrastructure).

Usage in a route (Astha's routes use this, not their own sessions):

    from sqlalchemy.orm import Session
    from app.db import get_db

    @router.get("/incidents/{incident_id}")
    def get_incident(incident_id: str, db: Session = Depends(get_db)) -> ...:
        ...

get_db() gives each request its own session and always closes it. Writes are
not committed automatically: call db.commit() once the whole operation has
succeeded, so a request that fails part-way leaves nothing behind (REQ-02).
"""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models (app/models.py)."""


@lru_cache
def get_engine() -> Engine:
    """Create the engine on first use, so importing the app needs no database."""
    # pool_pre_ping drops connections that died while idle (e.g. after a DB restart)
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request, rolled back on error, always closed."""
    session = get_session_factory()()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
