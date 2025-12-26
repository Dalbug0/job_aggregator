import datetime

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import UserRead

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

security = HTTPBearer()


def create_token(data: dict, expires_minutes: int = 30) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc)
    +datetime.timedelta(minutes=expires_minutes)
    to_encode.update(
        {"exp": expire, "iat": datetime.datetime.now(datetime.timezone.utc)}
    )
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


def create_tokens(user_id: int) -> dict:
    access_token = create_token(
        {"sub": str(user_id), "type": "access"}, expires_minutes=15
    )
    refresh_token = create_token(
        {"sub": str(user_id), "type": "refresh"}, expires_minutes=60 * 24
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def refresh_token(refresh_token: str) -> dict:
    try:
        payload = verify_token(refresh_token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return create_tokens(user_id)


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
