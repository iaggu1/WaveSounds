from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    port: int = 8000
    allowed_origins: str = "http://localhost:3000"
    trusted_proxy_ips: str = ""
    database_url: str
    resend_api_key: str = ""
    email_from: str = "convite@forma.audio"

    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[1] / ".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
