"""Fixtures for infrastructure tests.

Owner: Srihari. These tests run the app in-process (FastAPI TestClient) with a
known API key. Tests that touch the database need TEST_DATABASE_URL pointing at
a disposable PostgreSQL (they reset it); they are skipped otherwise, so they
can never wipe a real database by accident.
"""

import os
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import db as db_module
from app.config import get_settings

TEST_KEY = "infra-test-key"


def _clear_caches() -> None:
    get_settings.cache_clear()
    db_module.get_session_factory.cache_clear()
    db_module.get_engine.cache_clear()


@pytest.fixture
def settings_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Known settings for one test; the database URL is a dummy unless a test asks for one."""
    monkeypatch.setenv("API_KEY", TEST_KEY)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://unused:unused@127.0.0.1:1/unused")
    _clear_caches()
    yield
    _clear_caches()


@pytest.fixture
def app(settings_env: None) -> FastAPI:
    from app.main import create_app

    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def database(monkeypatch: pytest.MonkeyPatch, settings_env: None) -> Iterator[str]:
    """A migrated, empty test database (skips without TEST_DATABASE_URL)."""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; needs a disposable PostgreSQL")
    monkeypatch.setenv("DATABASE_URL", url)
    _clear_caches()

    from alembic import command
    from alembic.config import Config

    command.upgrade(Config("alembic.ini"), "head")
    from sqlalchemy import text

    with db_module.get_engine().begin() as conn:
        conn.execute(text("TRUNCATE TABLE evidence, incidents, test_sessions RESTART IDENTITY"))
    yield url
    _clear_caches()
