"""Application configuration.

Owner: Srihari (infrastructure).

Settings come from the environment (or a local .env file), never from source
code. Nothing is read at import time, so importing the app (for example to
generate the OpenAPI document) does not require DATABASE_URL or API_KEY.
"""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Field length limits. The contract leaves the maximum lengths of title and
# description to be agreed by both teams (docs/contract-issues.md #3), so they
# live here, in one place, until the pod settles on numbers.
TITLE_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 5000
SHORT_TEXT_MAX_LENGTH = 500


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # e.g. postgresql+psycopg://user:password@host:5432/dbname
    database_url: str
    # The shared key clients send in the X-API-Key header.
    api_key: SecretStr


@lru_cache
def get_settings() -> Settings:
    """Load settings once, the first time they are needed."""
    return Settings()  # values come from the environment
