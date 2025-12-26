from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import (
    authenticate_user,
    create_user,
    create_user_by_password,
    get_user_by_id,
)
from app.database import get_db
from app.schemas import (
    LoginResponse,
    LoginSchema,
    UserCreate,
    UserRead,
    UserRegisterResponse,
    UserRegisterSchema,
)
from app.services.auth import create_token

router = APIRouter(prefix="/users", tags=["users"])


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

    access_token = create_token({"sub": str(db_user.id)}, expires_minutes=15)
    refresh_token = create_token(
        {"sub": str(db_user.id)}, expires_minutes=60 * 24
    )

    return LoginResponse(
        access_token=access_token, refresh_token=refresh_token
    )


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    db_user = create_user(db, user)
    return UserRead.model_validate(db_user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserRead:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserRead.model_validate(db_user)
