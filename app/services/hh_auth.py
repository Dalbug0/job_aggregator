import httpx
from fastapi import HTTPException

from app.config import HHSettings
from app.models import HHToken


def exchange_code_for_token(code: str) -> dict:
    token_url = "https://hh.ru/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": HHSettings.hh_client_id,
        "client_secret": HHSettings.hh_client_secret,
        "code": code,
        "redirect_uri": HHSettings.hh_redirect_uri,
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
            "client_id": HHSettings.hh_client_id,
            "client_secret": HHSettings.hh_client_secret,
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
