# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.database import check_connection
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    print("Prilogenie ostanovleno")


app = FastAPI(title="Job Aggregator API", version="0.1.0", lifespan=lifespan)

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

@app.get("/vacancies")
def get_vacancies(
    db: Session = Depends(get_db),
    company: Optional[str] = None,
    location: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = Query("created_at", regex="(?i)^(created_at|title)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    query = db.query(Vacancy)

    if company:
        query = query.filter(Vacancy.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(Vacancy.location.ilike(f"%{location}%"))
    if keyword:
        query = query.filter(Vacancy.title.ilike(f"%{keyword}%"))

    sort_column = getattr(Vacancy, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()

    vacancies = query.order_by(sort_column).limit(limit).offset(offset).all()

    return [
        {
            "id": v.id,
            "title": v.title,
            "company": v.company,
            "location": v.location,
            "url": v.url,
            "created_at": v.created_at
        }
        for v in vacancies
    ]


@app.post("/load_vacancies")
def load_vacancies(keyword: str, area: int = 1002, db: Session = Depends(get_db)):
        items = fetch_vacancies(keyword, area)
        saved = []
        for item in items:
            saved.append(
                create_vacancy(
                    db,
                    title=item["name"],
                    company=item["employer"]["name"] if item.get("employer") else "N/A",
                    location=item["area"]["name"] if item.get("area") else "N/A",
                    url=item["alternate_url"]
                )
            )
        return {"saved_count": len(saved)}
    