from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import create_user, delete_user, get_user_by_id
from app.database import get_db
from app.schemas import UserCreate, UserRead
from app.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    db_user = create_user(db, user)
    return UserRead.model_validate(db_user)


@router.get("/current")
def get_current_user_info(current_user: UserRead = Depends(get_current_user)):
    return current_user


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
