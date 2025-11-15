from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.config import hh_settings
from app.database import get_db
from app.models import User
from app.models.hh_token import HHToken
from app.services.hh_auth import exchange_code_for_token, get_hh_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/hh/login")
def hh_login():
    params = {
        "response_type": "code",
        "client_id": hh_settings.hh_client_id,
        "redirect_uri": hh_settings.hh_redirect_uri,
    }
    url = f"https://hh.ru/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/hh/callback")
def hh_callback(code: str, db: Session = Depends(get_db)):
    tokens = exchange_code_for_token(code)
    user_id = 1  # TODO: заменить на текущего авторизованного пользователя

    db_token = HHToken(
        user_id=user_id,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )
    db.add(db_token)
    db.commit()

    return {"status": "ok"}


@router.get("/hh/resumes")
def get_resumes(access_token: str = Depends(get_hh_token)):
    response = httpx.get(
        "https://api.hh.ru/resumes/mine",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()


@router.post("/hh/resumes/select/{resume_id}")
def select_resume(
    resume_id: str, db: Session = Depends(get_db), user_id: int = 1
):  # Убрать значение по умолчанию для user_id когда закончю шифровку
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.active_resume_id = resume_id
    db.commit()
    return {"status": "ok", "active_resume_id": resume_id}


@router.post("/hh/resumes/{resume_id}/publish")
def publish_resume(resume_id: str, access_token: str = Depends(get_hh_token)):
    response = httpx.post(
        f"https://api.hh.ru/resumes/{resume_id}/publish",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to publish resume")
    return {"status": "ok", "message": "Resume published"}


@router.get("/hh/resumes/{resume_id}/vacancies")
def search_vacancies_by_resume(
    resume_id: str, access_token: str = Depends(get_hh_token)
):
    response = httpx.get(
        f"https://api.hh.ru/resumes/{resume_id}/similar_vacancies",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Failed to fetch vacancies"
        )
    return response.json()
