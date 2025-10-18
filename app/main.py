# app/main.py

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.database import check_connection
from app.exceptions import generic_exception_handler, http_exception_handler
from app.logger import logger
from app.routes import vacancies
from app.scheduler import fin_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Job Aggregator API started")

    logger.info("✅ Приложение готово")

    if os.getenv("DISABLE_SCHEDULER") != "1":
        start_scheduler()

    yield
    if os.getenv("DISABLE_SCHEDULER") != "1":
        fin_scheduler()
    print("Приложение остановленно.")


app = FastAPI(
    title="Vacancies API",
    description="API для управления вакансиями и интеграции с внешними сервисами",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)


app.include_router(vacancies.router, prefix="/vacancies", tags=["Vacancies"])

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
        return JSONResponse(status_code=503, content={"db": "unavailable", "detail": str(e)})
