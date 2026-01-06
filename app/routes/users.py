from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import (
    create_user,
    delete_user,
    get_user_by_id,
    create_telegram_user,
    get_telegram_user_by_telegram_id
)
from app.database import get_db
from app.schemas import UserCreate, UserRead
from app.schemas.user import TelegramUserRead, TelegramUserRegisterSchema
from app.services.auth import get_current_user_or_telegram  # type: ignore

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    db_user = create_user(db, user)
    return UserRead.model_validate(db_user)


@router.get("/current")
def get_current_user_info(current_user: UserRead = Depends(get_current_user_or_telegram)):
    return current_user


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Определяем тип пользователя и возвращаем соответствующую схему
    from app.models import TelegramUser
    if isinstance(db_user, TelegramUser):
        return TelegramUserRead.model_validate(db_user)
    else:
        return UserRead.model_validate(db_user)


@router.delete("/{user_id}")
def del_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> dict:
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "User deleted successfully"}


# Telegram-specific endpoints
@router.get("/telegram/{telegram_id}", response_model=TelegramUserRead)
def get_telegram_user(
    telegram_id: int,
    db: Session = Depends(get_db),
) -> TelegramUserRead:
    """Получить Telegram пользователя по telegram_id"""
    telegram_user = get_telegram_user_by_telegram_id(db, telegram_id)
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Telegram user not found"
        )
    return TelegramUserRead.model_validate(telegram_user)


@router.get("/telegram/user/{user_id}", response_model=TelegramUserRead)
def get_telegram_user_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
) -> TelegramUserRead:
    """Получить Telegram пользователя по user_id"""
    # Сначала получаем пользователя по user_id
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Проверяем, является ли пользователь TelegramUser
    from app.models import TelegramUser
    if not isinstance(user, TelegramUser):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User is not a Telegram user"
        )

    return TelegramUserRead.model_validate(user)


@router.post("/telegram/", response_model=TelegramUserRead, status_code=status.HTTP_201_CREATED)
def register_telegram_user(
    telegram_user: TelegramUserRegisterSchema,
    db: Session = Depends(get_db),
) -> TelegramUserRead:
    """Регистрация пользователя через Telegram"""
    db_telegram_user = create_telegram_user(db, telegram_user)
    return TelegramUserRead.model_validate(db_telegram_user)
