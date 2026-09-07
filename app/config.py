from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LogShield"
    database_url: str = "postgresql+psycopg2://logshield:logshield@db:5432/logshield"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    ingestion_api_key: str = "change-me-ingestion-key"
    webhook_urls: str = ""
    webhook_hmac_secret: str = "change-me-webhook-secret"
    brute_force_threshold: int = 5
    api_spike_threshold: int = 100

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def webhook_url_list(self) -> list[str]:
        return [url.strip() for url in self.webhook_urls.split(",") if url.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()