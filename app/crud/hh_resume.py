import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import ResumeCreate


def hh_request(method: str, url: str, token: str, **kwargs):
    response = httpx.request(
        method, url, headers={"Authorization": f"Bearer {token}"}, **kwargs
    )
    return response


def handle_hh_response(
    response, action: str = "resume", return_json: bool = False
):
    if response.status_code == 200 and return_json:
        return response.json()

    if response.status_code == 204:
        return {"status": "ok", "message": f"{action.capitalize()} successful"}

    if response.status_code == 400:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{action.capitalize()} невозможен. "
                "Ошибка в теле запроса или резюме "
                "не заполнено."
            ),
        )

    if response.status_code == 403:
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
