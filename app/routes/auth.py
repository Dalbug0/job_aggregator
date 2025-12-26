from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.user import authenticate_user, create_user_by_password
from app.database import get_db
from app.schemas import LoginSchema, UserRegisterSchema
from app.schemas.auth import (
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
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
