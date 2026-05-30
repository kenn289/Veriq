from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Description: Runtime configuration loaded from environment variables.
    Usage Example:
        settings = Settings()
    """

    app_name: str = "Veriq API"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://veriq:veriq@localhost:5432/veriq"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "veriq"
    minio_secret_key: str = "veriqsecret"
    minio_bucket: str = "veriq-artifacts"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    seed_roles_on_startup: bool = True
    # AI test generation settings
    test_generation_provider: str = "rule"  # 'rule' or 'model'
    llm_model_name: str | None = None
    llm_adapter_dir: str | None = None
    generation_defaults: dict | None = None

    model_config = SettingsConfigDict(env_prefix="VERIQ_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Description: Load and cache runtime settings.
    Parameters:
        None
    Returns:
        Settings: Cached settings object.
    Usage Example:
        settings = get_settings()
    """

    return Settings()
