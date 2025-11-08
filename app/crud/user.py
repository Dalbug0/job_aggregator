from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = (
        db.query(User).filter(User.username == user.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    if user.email:
        existing_email = (
            db.query(User).filter(User.email == user.email).first()
        )
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
