# tests/test_settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class TestConfig(BaseSettings):
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_pass"
    POSTGRES_DB: str = "job_aggregator_test"
    POSTGRES_PORT: int = 5433
    POSTGRES_HOST: str = "localhost"
    SECRET_KEY: str

    log_level: str = "DEBUG"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env.test", env_file_encoding="utf-8"
    )


class TestHHSettings(BaseSettings):
    hh_client_id: str
    hh_client_secret: str
    hh_redirect_uri: str

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
    )


test_settings = TestConfig()
