# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.database import check_connection
from app.database import Base, engine
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Vacancy
from app.services.hh_api import fetch_vacancies
from app.crud.vacancy import create_vacancy
from typing import Optional
from fastapi import Query
from app.scheduler import start_scheduler
from contextlib import asynccontextmanager
from app.routes import vacancies
from app.logger import logger
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from app.exceptions import http_exception_handler, generic_exception_handler




@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Job Aggregator API started")

    logger.info("🔄 Проверка и создание таблиц...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Таблицы готовы")

    start_scheduler()

    yield
    print("Приложение остановленно.")


app = FastAPI(title="Job Aggregator API", version="0.1.0", lifespan=lifespan)

app.include_router(vacancies.router, prefix="/vacancies", tags=["Vacancies"])
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health/db")
def health_db():
    try:
        check_connection()
        return {"db": "ok"}
    except Exception as e:
        # В проде логируй ошибку подробнее
        return JSONResponse(status_code=503, content={"db": "unavailable", "detail": str(e)})


    