from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import authenticate_user, create_telegram_user, create_user_by_password, get_telegram_user_by_telegram_id
from app.database import get_db
from app.exceptions import TelegramUserAlreadyExists
from app.logger import logger
from app.schemas import LoginSchema, UserRegisterSchema
from app.schemas.user import TelegramUserRegisterSchema
from app.schemas.auth import (
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TelegramUserRegisterResponse,
    UserRegisterResponse,
)
from app.services.auth import create_tokens, refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRegisterResponse)
def register(
    user: UserRegisterSchema, db: Session = Depends(get_db)
) -> UserRegisterResponse:
    base_user = create_user_by_password(db, user)
    return UserRegisterResponse(status="ok", user_id=base_user.id)


@router.post("/register/telegram", response_model=TelegramUserRegisterResponse)
def register_telegram(
    telegram_user: TelegramUserRegisterSchema, db: Session = Depends(get_db)
):
    """Регистрация пользователя через Telegram"""
    logger.info(f"Attempting to register Telegram user: {telegram_user.telegram_id}")

    # Проверяем, не существует ли уже пользователь
    from app.crud.user import get_telegram_user_by_telegram_id
    existing_user = get_telegram_user_by_telegram_id(db, telegram_user.telegram_id)
    if existing_user:
        logger.warning(f"Telegram user already exists: {telegram_user.telegram_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_id {telegram_user.telegram_id} already exists"
        )

    try:
        from app.crud.user import create_telegram_user
        db_telegram_user = create_telegram_user(db, telegram_user)
        logger.info(f"Successfully registered Telegram user: {telegram_user.telegram_id} -> user_id: {db_telegram_user.id}")
        return TelegramUserRegisterResponse(
            status="ok",
            user_id=db_telegram_user.id,
            telegram_id=db_telegram_user.telegram_id
        )
    except Exception as e:
        logger.error(f"Unexpected error in register_telegram: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


@router.post("/login", response_model=LoginResponse)
def login(user: LoginSchema, db: Session = Depends(get_db)) -> LoginResponse:
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    tokens = create_tokens(db_user.id, db)
    return LoginResponse(**tokens)


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_access_token(
    request: RefreshTokenRequest, db: Session = Depends(get_db)
) -> RefreshTokenResponse:
    tokens = refresh_token(request.refresh_token, db)
    return RefreshTokenResponse(**tokens)
