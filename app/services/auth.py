import datetime

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.auth import (
    get_refresh_token,
    invalidate_user_refresh_tokens,
    save_refresh_token,
)
from app.database import get_db
from app.logger import logger
from app.models import User
from app.schemas import UserRead

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()


def create_token(data: dict, expires_minutes: int = 30) -> str:
    to_encode = data.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    expire = now + datetime.timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def create_tokens(user_id: int, db: Session) -> dict:
    access_token = create_token(
        {"sub": str(user_id), "type": "access"},
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token_value = create_token(
        {"sub": str(user_id), "type": "refresh"},
        expires_minutes=REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    refresh_expires_at = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    save_refresh_token(db, user_id, refresh_token_value, refresh_expires_at)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
    }


def refresh_token(refresh_token: str, db: Session) -> dict:
    logger.info("Starting token refresh process")

    try:
        payload = verify_token(refresh_token)
        user_id = int(payload.get("sub"))
        logger.info(f"Token verified successfully for user_id: {user_id}")
    except Exception as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db_token = get_refresh_token(db, refresh_token)
    if not db_token or db_token.user_id != user_id:
        logger.warning(
            f"Database token validation failed for user_id: {user_id}"
        )
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    logger.info(f"Invalidating existing refresh tokens for user_id: {user_id}")
    invalidate_user_refresh_tokens(db, user_id)

    logger.info(f"Creating new tokens for user_id: {user_id}")
    return create_tokens(user_id, db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> UserRead:
    token = credentials.credentials
    try:
        payload = verify_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)
