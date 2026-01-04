import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import ResumeCreate


def hh_request(method: str, url: str, token: str, **kwargs):
    from app.logger import logger
    # Согласно документации HH.ru: User-Agent обязателен, рекомендуется указать название приложения и email
    # Формат: MyApp/1.0 (my-app-feedback@example.com)
    # Используем название приложения из HH.ru API: "Job Aggregator API"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Job Aggregator API/1.0 (pinsk.m.alibaba@gmail.com)",
    }
    # Логируем первые и последние символы токена для диагностики (безопасно)
    token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "***"
    logger.debug(f"Making HH.ru API request: {method} {url} with token: {token_preview}")
    response = httpx.request(method, url, headers=headers, **kwargs)
    logger.debug(f"HH.ru API response status: {response.status_code} for {url}")
    return response


def handle_hh_response(
    response, action: str = "resume", return_json: bool = False
):
    if response.status_code == 200 and return_json:
        return response.json()

    if response.status_code == 204:
        return {"status": "ok", "message": f"{action.capitalize()} successful"}

    if response.status_code == 400:
        from app.logger import logger
        error_text = response.text[:500] if response.text else "No response text"
        logger.error(f"HH.ru API returned 400 for {action}. Response: {error_text}")
        raise HTTPException(
            status_code=400,
            detail=(
                f"{action.capitalize()} невозможен. "
                "Ошибка в теле запроса или резюме "
                "не заполнено. "
                f"Details: {error_text}"
            ),
        )

    if response.status_code == 403:
        from app.logger import logger
        logger.error(f"HH.ru API returned 403 for {action}. Response: {response.text}")
        raise HTTPException(
            status_code=403,
            detail=(
                "Ошибка авторизации. "
                "Убедитесь, что токен действителен "
                "и пользователь является соискателем."
            ),
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=(
                f"{action.capitalize()} объект не существует "
                "или недоступен для текущего пользователя."
            ),
        )

    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail=(
                f"{action.capitalize()} временно недоступно. "
                "Попробуйте позже."
            ),
        )

    raise HTTPException(
        status_code=response.status_code,
        detail=(f"Неизвестная ошибка при {action}: " f"{response.text}"),
    )


def get_resumes(access_token: str) -> dict:
    response = hh_request(
        method="GET",
        url="https://api.hh.ru/resumes/mine",
        token=access_token,
    )
    return handle_hh_response(response, action="get resumes", return_json=True)


def select_active_resume(db: Session, user_id: int, resume_id: str) -> dict:
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.active_resume_id = resume_id
    db.commit()
    return {"status": "ok", "active_resume_id": resume_id}


def publish_resume(resume_id: str, access_token: str) -> dict:
    response = hh_request(
        method="POST",
        url=f"https://api.hh.ru/resumes/{resume_id}/publish",
        token=access_token,
    )
    return handle_hh_response(response, action="publish resume")


def search_vacancies_by_resume(resume_id: str, access_token: str) -> dict:
    response = hh_request(
        method="GET",
        url=f"https://api.hh.ru/resumes/{resume_id}/similar_vacancies",
        token=access_token,
    )
    return handle_hh_response(
        response, action="search vacancies", return_json=True
    )


def search_vacancies_by_active_resume(
    db: Session, user_id: int, access_token: str
) -> dict:
    user = db.query(User).get(user_id)
    if not user or not user.active_resume_id:
        raise HTTPException(
            status_code=404, detail="No active resume selected"
        )
    return search_vacancies_by_resume(user.active_resume_id, access_token)


def create_resume(payload: ResumeCreate, access_token: str) -> dict:
    payload_dict = payload.model_dump(exclude_unset=True)
    response = hh_request(
        method="POST",
        url="https://api.hh.ru/resume_profile",
        token=access_token,
        json=payload_dict,
    )
    return handle_hh_response(
        response, action="create resume", return_json=True
    )


def get_active_resume(db: Session, user_id: int, access_token: str) -> dict:
    user = db.query(User).get(user_id)
    if not user or not user.active_resume_id:
        raise HTTPException(
            status_code=404, detail="No active resume selected"
        )

    response = hh_request(
        method="GET",
        url=f"https://api.hh.ru/resumes/{user.active_resume_id}",
        token=access_token,
    )
    return handle_hh_response(
        response, action="get active resume", return_json=True
    )


def update_resume(resume_id: str, payload: dict, access_token: str):
    response = hh_request(
        method="PUT",
        url=f"https://api.hh.ru/resumes/{resume_id}",
        token=access_token,
        json=payload,
    )
    return handle_hh_response(response, action="update resume")


def delete_resume(resume_id: str, access_token: str) -> dict:
    response = hh_request(
        method="DELETE",
        url=f"https://api.hh.ru/resumes/{resume_id}",
        token=access_token,
    )
    return handle_hh_response(response, action="delete resume")
