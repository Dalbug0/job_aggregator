# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.database import check_connection

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
