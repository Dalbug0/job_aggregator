# tests/conftest.py
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.test_settings import test_settings


def is_test_db_available():
    import time

    from sqlalchemy import text

    # Пытаемся подключиться несколько раз с задержками
    for attempt in range(3):
        try:
            engine = create_engine(
                test_settings.database_url, connect_args={"connect_timeout": 5}
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            if attempt < 2:  # Не последняя попытка
                time.sleep(2)  # Ждем 2 секунды перед следующей попыткой
            else:
                print(
                    "Не удалось подключиться "
                    "к тестовой БД после 3 попыток: {e}"
                )
                return False


@pytest.fixture(scope="session")
def test_db():
    if not is_test_db_available():
        pytest.skip(
            "Тестовая база данных PostgreSQL недоступна. "
            "Запустите: docker-compose -f docker-compose.test.yml up -d"
        )

    engine = create_engine(test_settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_session(test_db):
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_session):
    def override_get_db():
        try:
            yield test_session
        finally:
            pass

    # Disable scheduler and migrations in tests

    old_scheduler = os.environ.get("DISABLE_SCHEDULER")
    old_migrations = os.environ.get("DISABLE_MIGRATIONS")
    os.environ["DISABLE_SCHEDULER"] = "1"
    os.environ["DISABLE_MIGRATIONS"] = "1"

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

    # Restore original values
    if old_scheduler is not None:
        os.environ["DISABLE_SCHEDULER"] = old_scheduler
    else:
        os.environ.pop("DISABLE_SCHEDULER", None)

    if old_migrations is not None:
        os.environ["DISABLE_MIGRATIONS"] = old_migrations
    else:
        os.environ.pop("DISABLE_MIGRATIONS", None)
