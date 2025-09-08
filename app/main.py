# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.database import check_connection
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Vacancy

app = FastAPI(title="Job Aggregator API", version="0.1.0")

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
def get_vacancies(db: Session = Depends(get_db)):
    vacancies = db.query(Vacancy).all() 
    return [
        {
            "id": v.id,
            "title": v.title,
            "company": v.company,
            "location": v.location,
            "url": v.url
        }
        for v in vacancies
    ]