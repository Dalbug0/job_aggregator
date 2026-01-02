# app/main.py

import os
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.database import check_connection
from app.exceptions import generic_exception_handler, http_exception_handler
from app.logger import logger
from app.routes import auth, hh_auth, users, vacancies
from app.scheduler import fin_scheduler, start_scheduler


def run_migrations():
    """Run database migrations automatically on startup."""
    try:
        logger.info("🔄 Running database migrations...")
        # Get the directory of the current file (main.py is in app/)
        # alembic.ini is in the project root, so we go up one level
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_cfg = Config(os.path.join(project_root, "alembic.ini"))

        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Database migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Failed to run migrations: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Job Aggregator API started")

    # Run database migrations
    run_migrations()

    logger.info("✅ Приложение готово")

    if os.getenv("DISABLE_SCHEDULER") != "1":
        start_scheduler()

    yield
    if os.getenv("DISABLE_SCHEDULER") != "1":
        fin_scheduler()
    print("Приложение остановленно.")


app = FastAPI(
    title="Vacancies API",
    description="API для управления вакансиями и"
    "интеграции с внешними сервисами",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan,
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vacancies.router)
app.include_router(hh_auth.router)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        check_connection()
        return {"db": "ok"}
    except Exception as e:
        return JSONResponse(
            status_code=503, content={"db": "unavailable", "detail": str(e)}
        )
