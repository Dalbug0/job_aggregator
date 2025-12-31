from argon2 import PasswordHasher
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserAuth
from app.schemas import UserCreate, UserRegisterSchema

ph = PasswordHasher()


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = (
        db.query(User).filter(User.username == user.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def create_user_by_password(db: Session, user: UserRegisterSchema) -> User:
    base_user = create_user(
        db, UserCreate(username=user.username, email=user.email)
    )

    hashed_password = ph.hash(user.password)

    if base_user.auth:
        base_user.auth.password_hash = hashed_password
    else:
        auth_user = UserAuth(id=base_user.id, password_hash=hashed_password)
        db.add(auth_user)

    db.commit()
    return base_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user_auth = (
        db.query(UserAuth)
        .join(User, UserAuth.id == User.id)
        .filter(User.email == email)
        .first()
    )
    if not user_auth:
        return None

    try:
        ph.verify(user_auth.password_hash, password)
        return user_auth.user
    except Exception:
        return None


def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    if user.auth:
        db.delete(user.auth)

    db.delete(user)
    db.commit()
    return True
