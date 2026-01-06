import base64
import json
import time
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.config import hh_settings
from app.crud.hh_resume import (
    create_resume,
    delete_resume,
    get_active_resume,
    get_current_user_info,
    get_resumes,
    publish_resume,
    search_vacancies_by_active_resume,
    search_vacancies_by_resume,
    select_active_resume,
    update_resume,
)
from app.crud.hh_token import save_hh_token
from app.crud.user import get_user_by_id
from app.database import get_db
from app.schemas import ResumeCreate, UserRead
from app.services.auth import get_current_user
from app.services.hh_auth import get_hh_token
from app.models.hh_token import HHToken

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# Fixed routes first
@router.get("/hh/login")
def hh_login(user_id: int = Query(..., description="User ID for OAuth state")):
    state_data = {"user_id": user_id, "timestamp": int(time.time())}
    state_json = json.dumps(state_data)
    state = base64.urlsafe_b64encode(state_json.encode()).decode()

    params = {
        "response_type": "code",
        "client_id": hh_settings.hh_client_id,
        "redirect_uri": hh_settings.hh_redirect_uri,
        "state": state,
    }
    url = f"https://hh.ru/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/hh/login_url")
def get_hh_login_url(user_id: int = Query(..., description="User ID for OAuth state")):
    """Get HH.ru authorization URL without redirect (for bots and API clients)"""
    state_data = {"user_id": user_id, "timestamp": int(time.time())}
    state_json = json.dumps(state_data)
    state = base64.urlsafe_b64encode(state_json.encode()).decode()

    params = {
        "response_type": "code",
        "client_id": hh_settings.hh_client_id,
        "redirect_uri": hh_settings.hh_redirect_uri,
        "state": state,
    }
    url = f"https://hh.ru/oauth/authorize?{urlencode(params)}"
    return {"login_url": url}


@router.get("/hh/callback")
def hh_callback(
    code: str,
    state: str = Query(..., description="OAuth state parameter"),
    db: Session = Depends(get_db),
):
    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State parameter is required",
        )

    try:
        state_json = base64.urlsafe_b64decode(state.encode()).decode()
        state_data = json.loads(state_json)
        user_id = state_data["user_id"]
        timestamp = state_data["timestamp"]
    except (ValueError, KeyError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        )

    current_time = int(time.time())
    if current_time - timestamp > 900:  # 15 minutes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State parameter expired. Please generate a new login URL.",
        )

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    save_hh_token(db, user_id, code)
    return {"status": "ok", "message": "HH.ru token saved successfully"}


@router.get("/hh/token/{user_id}")
def get_hh_token_status(
    user_id: int,
    db: Session = Depends(get_db)
):

    token = db.query(HHToken).filter_by(user_id=user_id).first()
    if not token:
        return {"status": "not_found", "user_id": user_id}

    return {
        "status": "found",
        "user_id": user_id,
        "created_at": token.created_at,
        "expires_in": token.expires_in,
        "has_access_token": token.access_token is not None,
        "has_refresh_token": token.refresh_token is not None
    }


@router.get("/hh/me")
def get_current_user_info_endpoint(access_token: str = Depends(get_hh_token)):
    return get_current_user_info(access_token)


@router.get("/hh/resumes")
def get_resumes_endpoint(access_token: str = Depends(get_hh_token)):
    return get_resumes(access_token)


@router.post("/hh/resumes/test_create")
def create_test_resume_endpoint(access_token: str = Depends(get_hh_token)):
    """Создать тестовое резюме с фиксированными данными"""
    # Тестовые данные для создания резюме
    test_resume_data = {
        "title": "Python разработчик (тестовое резюме)",
        "area": {
            "id": "1"  # Москва
        },
        "salary": {
            "amount": 150000,
            "currency": "RUR"
        },
        "employment": {
            "id": "full"  # Полная занятость
        },
        "schedule": {
            "id": "fullDay"  # Полный день
        },
        "experience": {
            "id": "between1And3"  # 1-3 года
        },
        "education_level": {
            "id": "higher"  # Высшее
        },
        "skills": "Python, Django, PostgreSQL, Git",
        "about": "Опытный Python разработчик с опытом работы в веб-разработке",
        "contacts": {
            "email": "test@example.com",
            "phone": "+7 (999) 123-45-67"
        }
    }
    return create_resume(test_resume_data, access_token)


@router.post("/hh/resumes/create_resume")
def create_resume_endpoint(
    payload: ResumeCreate,
    access_token: str = Depends(get_hh_token)
):
    return create_resume(payload, access_token)
    # TODO
    # Обработку дозаполнения схему резюме‑профиля —
    # это JSON‑структура с полями, которые нужно(обязательно\необязательно)
    # заполнить (ФИО, контакты, опыт работы, образование, навыки и т.д.).


@router.get("/hh/resumes/active")
def get_active_resume_endpoint(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    access_token: str = Depends(get_hh_token),
):
    return get_active_resume(db, current_user.id, access_token)


@router.get("/hh/resumes/active/vacancies")
def search_vacancies_by_active_resume_endpoint(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    access_token: str = Depends(get_hh_token),
):
    return search_vacancies_by_active_resume(db, current_user.id, access_token)


# Then template routes
@router.post("/hh/resumes/select/{resume_id}")
def select_resume(
    resume_id: str,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return select_active_resume(db, current_user.id, resume_id)


@router.post("/hh/resumes/{resume_id}/publish")
def publish_resume_endpoint(
    resume_id: str,
    access_token: str = Depends(get_hh_token)
):
    return publish_resume(resume_id, access_token)


@router.get("/hh/resumes/{resume_id}/vacancies")
def search_vacancies_by_resume_endpoint(
    resume_id: str,
    access_token: str = Depends(get_hh_token)
):
    return search_vacancies_by_resume(resume_id, access_token)


@router.put("/hh/resumes/{resume_id}")
def update_resume_endpoint(
    resume_id: str,
    payload: dict,
    access_token: str = Depends(get_hh_token)
):
    return update_resume(resume_id, payload, access_token)


@router.delete("/hh/resumes/{resume_id}")
def delete_resume_endpoint(
    resume_id: str,
    access_token: str = Depends(get_hh_token)
):
    return delete_resume(resume_id, access_token)
