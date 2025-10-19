# tests/test_settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class TestConfig(BaseSettings):
    """Конфигурация для тестовой среды"""

    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_pass"
    POSTGRES_DB: str = "job_aggregator_test"
    POSTGRES_PORT: int = 5433  # Другой порт для тестовой БД
    POSTGRES_HOST: str = "localhost"

    log_level: str = "DEBUG"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env.test", env_file_encoding="utf-8")


test_settings = TestConfig()
