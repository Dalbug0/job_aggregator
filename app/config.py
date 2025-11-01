# app/config.py
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

_env = os.getenv("APP_ENV", "dev")
_env_file = ".env.prod" if _env == "prod" else ".env.dev"


class Settings(BaseSettings):
    # Optional full DSN override; if provided, use this exactly as given
    DATABASE_URL: str | None = None

    # Fallback parts for composing the DSN when DATABASE_URL is not provided
    POSTGRES_USER: str = "jobuser"
    POSTGRES_PASSWORD: str = "jobpass"
    POSTGRES_DB: str = "job_aggregator"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "db"

    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Choose env file based on APP_ENV (dev/prod), default to .env.dev for local
    _env = os.getenv("APP_ENV", "dev")
    _env_file = ".env.prod" if _env == "prod" else ".env.dev"
    model_config = SettingsConfigDict(
        env_file=_env_file, env_file_encoding="utf-8"
    )


class HHSettings(BaseSettings):
    hh_client_id: str
    hh_client_secret: str
    hh_redirect_uri: str

    class Config:
        model_config = SettingsConfigDict(
            env_file=_env_file,
            env_file_encoding="utf-8",
            env_nested_delimiter="_",
        )


settings = Settings()
hh_settings = HHSettings()
