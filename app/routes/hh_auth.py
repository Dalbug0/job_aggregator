from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.config import hh_settings
from app.crud.hh_resume import (
    create_resume,
    delete_resume,
    get_active_resume,
    get_resumes,
    publish_resume,
    search_vacancies_by_active_resume,
    search_vacancies_by_resume,
    select_active_resume,
    update_resume,
)
from app.crud.hh_token import save_hh_token
from app.database import get_db
from app.schemas.hh_resume import ResumeCreate
from app.services.hh_auth import get_hh_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# Fixed routes first
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
    user_id = 1  # TODO: заменить на текущего авторизованного пользователя
    save_hh_token(db, user_id, code)
    return {"status": "ok"}


@router.get("/hh/resumes")
def get_resumes_endpoint(access_token: str = Depends(get_hh_token)):
    return get_resumes(access_token)


@router.post("/hh/resumes/create_resume")
def create_resume_endpoint(
    payload: ResumeCreate, access_token: str = Depends(get_hh_token)
):
    return create_resume(payload, access_token)
    # TODO
    # Обработку дозаполнения схему резюме‑профиля —
    # это JSON‑структура с полями, которые нужно(обязательно\необязательно)
    # заполнить (ФИО, контакты, опыт работы, образование, навыки и т.д.).


@router.get("/hh/resumes/active")
def get_active_resume_endpoint(
    db: Session = Depends(get_db),
    user_id: int = 1,
    access_token: str = Depends(get_hh_token),
):
    return get_active_resume(db, user_id, access_token)


@router.get("/hh/resumes/active/vacancies")
def search_vacancies_by_active_resume_endpoint(
    db: Session = Depends(get_db),
    user_id: int = 1,
    access_token: str = Depends(get_hh_token),
):
    return search_vacancies_by_active_resume(db, user_id, access_token)


# Then template routes
@router.post("/hh/resumes/select/{resume_id}")
def select_resume(
    resume_id: str, db: Session = Depends(get_db), user_id: int = 1
):  # Убрать значение по умолчанию для user_id когда закончю шифровку
    return select_active_resume(db, user_id, resume_id)


@router.post("/hh/resumes/{resume_id}/publish")
def publish_resume_endpoint(
    resume_id: str, access_token: str = Depends(get_hh_token)
):
    return publish_resume(resume_id, access_token)


@router.get("/hh/resumes/{resume_id}/vacancies")
def search_vacancies_by_resume_endpoint(
    resume_id: str, access_token: str = Depends(get_hh_token)
):
    return search_vacancies_by_resume(resume_id, access_token)


@router.put("/hh/resumes/{resume_id}")
def update_resume_endpoint(
    resume_id: str, payload: dict, access_token: str = Depends(get_hh_token)
):
    return update_resume(resume_id, payload, access_token)


@router.delete("/hh/resumes/{resume_id}")
def delete_resume_endpoint(
    resume_id: str, access_token: str = Depends(get_hh_token)
):
    return delete_resume(resume_id, access_token)
