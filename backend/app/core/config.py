from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / ".env"


class Settings(BaseSettings):
    """Typed config loaded from the environment and optional repo-root `.env`."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.is_file() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_user: str = "tracker"
    postgres_password: str = "changeme"
    postgres_db: str = "exercise_tracker"
    # Local Uvicorn: host is localhost (repo-root .env). Compose overrides this
    # for the api container so the hostname is the `db` service, not localhost.
    database_url: str = (
        "postgresql+psycopg://tracker:changeme@localhost:5432/exercise_tracker"
    )
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [part.strip() for part in self.cors_origins.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
