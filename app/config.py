# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "jobuser"
    POSTGRES_PASSWORD: str = "jobpass"
    POSTGRES_DB: str = "job_aggregator"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"  # если FastAPI будет в Docker, поменяем на "db"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
