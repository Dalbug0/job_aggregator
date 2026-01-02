import time

import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import hh_settings
from app.database import get_db
from app.models.hh_token import HHToken
from app.schemas import UserRead
from app.services.auth import get_current_user


def exchange_code_for_token(code: str) -> dict:
    token_url = "https://api.hh.ru/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": hh_settings.hh_client_id,
        "client_secret": hh_settings.hh_client_secret,
        "code": code,
        "redirect_uri": hh_settings.hh_redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = httpx.post(token_url, data=data, headers=headers)
    if response.status_code != 200:
        error_detail = response.text or "OAuth2 exchange failed"
        raise HTTPException(status_code=400, detail=error_detail)
    return response.json()


def refresh_hh_token(user_id: int, db):
    token = db.query(HHToken).filter_by(user_id=user_id).first()
    if not token:
        raise HTTPException(status_code=401, detail="No hh.ru token found")

    token_url = "https://api.hh.ru/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
        "client_id": hh_settings.hh_client_id,
        "client_secret": hh_settings.hh_client_secret,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = httpx.post(token_url, data=data, headers=headers)
    if response.status_code != 200:
        error_detail = response.text or "Failed to refresh token"
        raise HTTPException(status_code=400, detail=error_detail)

    new_tokens = response.json()
    token.access_token = new_tokens["access_token"]
    token.refresh_token = new_tokens.get("refresh_token", token.refresh_token)
    token.expires_in = new_tokens["expires_in"]
    db.commit()
    db.refresh(token)
    return token


def expired(token_info: HHToken) -> bool:
    expire_timestamp = (
        token_info.created_at.timestamp() + token_info.expires_in
    )
    return time.time() > expire_timestamp


def get_hh_token(current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
    token = db.query(HHToken).filter_by(user_id=current_user.id).first()
    if not token:
        raise HTTPException(
            status_code=401, detail="hh.ru account not connected"
        )

    if expired(token):
        token = refresh_hh_token(current_user.id, db)

    return token.access_token
