from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # для работы с SQLAlchemy моделей
