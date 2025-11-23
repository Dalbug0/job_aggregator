# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.test_settings import test_settings


def is_test_db_available():
    try:
        from sqlalchemy import text

        engine = create_engine(test_settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
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

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
