import os
from typing import List, Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.crud.vacancy import (
    create_vacancy,
    delete_vacancy,
    get_vacancies,
    list_vacancies,
    update_vacancy,
)
from app.database import get_db
from app.models import HHToken
from app.schemas.vacancy import (
    VacancyCreate,
    VacancyDelete,
    VacancyRead,
    VacancyUpdate,
)

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])

CLIENT_ID = os.getenv(
    "HH_CLIENT_ID", "HH_default_id"
)  # TODO: replace with your client id
REDIRECT_URI = os.getenv(
    "HH_REDIRECT_URI", "http://localhost:8000/api/v1/auth/hh/callback"
)  # TODO: replace with your redirect uri
CLIENT_SECRET = os.getenv(
    "HH_CLIENT_SECRET", "HH_your_client_secret"
)  # TODO: replace with your client secret


@router.get("/", response_model=List[VacancyRead])
def get_vacancies_list(
    company: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    db: Session = Depends(get_db),
):
    if company or location:
        return list_vacancies(db, sort_by, company, location, skip, limit)
    return get_vacancies(db, skip=skip, limit=limit)


@router.get("/hh/login")
def hh_login():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    url = f"https://hh.ru/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/hh/callback")
def hh_callback(code: str, db: Session = Depends(get_db)):
    token_url = "https://hh.ru/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = httpx.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="OAuth2 exchange failed")

    tokens = response.json()
    # tokens = {"access_token": "...", "refresh_token": "...", "expires_in": 3600}

    # Привязка к пользователю (упрощённо)
    user_id = 1  # TODO: заменить на текущего авторизованного пользователя
    db_token = HHToken(
        user_id=user_id,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )
    db.add(db_token)
    db.commit()
    return {"status": "ok", "tokens": tokens}


@router.post("/", response_model=VacancyRead)
def add_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db)):
    return create_vacancy(db, vacancy)


@router.put("/{vacancy_id}", response_model=VacancyRead)
def up_vacancy(
    vacancy_id: int, vacancy: VacancyUpdate, db: Session = Depends(get_db)
):
    return update_vacancy(db, vacancy_id, vacancy)


@router.delete("/{vacancy_id}", response_model=VacancyDelete)
def del_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    return delete_vacancy(db, vacancy_id)
