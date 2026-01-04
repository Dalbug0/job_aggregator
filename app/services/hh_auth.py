import time
from datetime import datetime, timezone

import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import hh_settings
from app.database import get_db
from app.logger import logger
from app.models.hh_token import HHToken
from app.schemas import UserRead
from app.services.auth import get_current_user_or_telegram


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
        logger.error(f"Failed to exchange authorization code for token. Status: {response.status_code}, Response: {error_detail}")
        raise HTTPException(status_code=400, detail=error_detail)
    logger.info("Successfully exchanged authorization code for token")
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
    # Обновляем created_at для правильного вычисления expired
    token.created_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(token)
    return token


def expired(token_info: HHToken) -> bool:
    # created_at - это datetime объект, timestamp() возвращает UTC timestamp
    # expires_in - количество секунд до истечения токена
    # time.time() - текущее время в секундах (UTC)
    if not token_info.created_at:
        logger.warning("Token has no created_at, considering expired")
        return True
    
    expire_timestamp = (
        token_info.created_at.timestamp() + token_info.expires_in
    )
    is_expired = time.time() > expire_timestamp
    logger.debug(f"Token expiration check: created_at={token_info.created_at}, expires_in={token_info.expires_in}s, expire_timestamp={expire_timestamp}, current_time={time.time()}, is_expired={is_expired}")
    return is_expired


def get_hh_token(current_user: UserRead = Depends(get_current_user_or_telegram), db: Session = Depends(get_db)):
    logger.info(f"get_hh_token called for user: {current_user.id} (username: {current_user.username})")

    token = db.query(HHToken).filter_by(user_id=current_user.id).first()
    if not token:
        logger.error(f"No HH token found for user {current_user.id}. Available tokens for users: {[t.user_id for t in db.query(HHToken).all()]}")
        raise HTTPException(
            status_code=401, detail="hh.ru account not connected"
        )

    logger.info(f"Found HH token for user {current_user.id}, created_at: {token.created_at}, expires_in: {token.expires_in}")
    
    if expired(token):
        logger.info(f"Token expired for user {current_user.id}, refreshing...")
        token = refresh_hh_token(current_user.id, db)
    else:
        logger.info(f"Token still valid for user {current_user.id}")
    
    # Логируем первые и последние символы токена для диагностики
    token_preview = f"{token.access_token[:10]}...{token.access_token[-10:]}" if len(token.access_token) > 20 else "***"
    logger.info(f"Returning access token for user {current_user.id}: {token_preview}")
    return token.access_token
