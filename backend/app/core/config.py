from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_name: str = "catalogue-api"
    debug: bool = False
    database_url: str  # e.g. postgresql+asyncpg://user:pass@localhost/db
    # validate protected urls by token
    internal_token: str


# S3 specific settings, keep separate for convenience
class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")
    s3_root_user: str
    s3_root_password: str
    s3_url: str
    s3_bucket_name: str

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_settings_s3() -> S3Settings:
    return S3Settings()
