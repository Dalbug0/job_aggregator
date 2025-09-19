# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    POSTGRES_USER: str = "jobuser"
    POSTGRES_PASSWORD: str = "jobpass"
    POSTGRES_DB: str = "job_aggregator"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "db" 

    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Choose env file based on APP_ENV (dev/prod), default to .env.dev for local
    _env = os.getenv("APP_ENV", "dev")
    _env_file = ".env.prod" if _env == "prod" else ".env.dev"
    model_config = SettingsConfigDict(env_file=_env_file, env_file_encoding="utf-8")

settings = Settings()
