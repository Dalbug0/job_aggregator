import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import hh_settings
from app.database import get_db
from app.models.hh_token import HHToken


def exchange_code_for_token(code: str) -> dict:
    token_url = "https://hh.ru/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": hh_settings.hh_client_id,
        "client_secret": hh_settings.hh_client_secret,
        "code": code,
        "redirect_uri": hh_settings.hh_redirect_uri,
    }
    response = httpx.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="OAuth2 exchange failed")
    return response.json()


def refresh_hh_token(user_id: int, db):
    token = db.query(HHToken).filter_by(user_id=user_id).first()
    if not token:
        raise HTTPException(status_code=401, detail="No hh.ru token found")

    response = httpx.post(
        "https://hh.ru/oauth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": hh_settings.hh_client_id,
            "client_secret": hh_settings.hh_client_secret,
        },
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to refresh token")

    new_tokens = response.json()
    token.access_token = new_tokens["access_token"]
    token.refresh_token = new_tokens.get("refresh_token", token.refresh_token)
    token.expires_in = new_tokens["expires_in"]
    db.commit()
    db.refresh(token)
    return token


def get_hh_token(user_id: int = 1, db: Session = Depends(get_db)):
    token = db.query(HHToken).filter_by(user_id=user_id).first()
    if not token:
        raise HTTPException(
            status_code=401, detail="hh.ru account not connected"
        )

    # TODO: проверить срок действия и обновить при необходимости
    # if expired(token):
    #     token = refresh_hh_token(user_id, db)

    return token.access_token
