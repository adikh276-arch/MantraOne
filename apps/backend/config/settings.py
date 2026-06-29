from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_version: str = "0.1.0"
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://mantraone:mantraone_dev_password@localhost:5432/mantraone_dev"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30

    redis_url: str = "redis://localhost:6379"
    redis_max_connections: int = 20

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.3

    encryption_key: str = ""

    local_dev_mode: bool = True
    firebase_mock_enabled: bool = True
    local_storage_path: str = "/tmp/mantraone_storage"  # nosec B108

    rate_limit_requests_per_minute: int = 60
    rate_limit_uploads_per_minute: int = 10

    coordinator_checkin_hour: int = 6
    max_checkins_per_day: int = 2

    watcher_lookback_hours: int = 48
    watcher_evaluation_interval_minutes: int = 60

    escalation_cooldown_days: int = 7

    cognee_db_path: str = "/tmp/mantraone_cognee"  # nosec B108
    signed_url_ttl_seconds: int = 900
    max_upload_size_bytes: int = 20 * 1024 * 1024

    @property
    @computed_field
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    @computed_field
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    @computed_field
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
