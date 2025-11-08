# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Получает текущего авторизованного пользователя из токена.

    В текущей реализации используется простой подход:
    - Токен содержит user_id в payload
    - Для полной реализации нужно добавить JWT декодирование

    TODO: Реализовать полноценную JWT аутентификацию
    """
    token = credentials.credentials

    # Временная реализация: токен = user_id
    # Для продакшена нужно использовать JWT с декодированием
    try:
        user_id = int(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_id(
    current_user: User = Depends(get_current_user),
) -> int:
    """Возвращает ID текущего пользователя."""
    return current_user.id
