from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.config import hh_settings
from app.database import get_db
from app.models import HHToken
from app.services.hh_auth import exchange_code_for_token

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

    return {"status": "ok"}  # лучше не возвращать все токены наружу
