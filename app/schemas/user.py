from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


# Для сценария без пароля (импорт пользователй)
class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime
    active_resume_id: Optional[str] = None

    class Config:
        from_attributes = True  # для работы с SQLAlchemy моделей


class UserRegisterSchema(UserBase):
    password: constr(min_length=8, max_length=128)
