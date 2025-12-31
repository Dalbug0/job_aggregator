from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, constr


class UserBase(BaseModel):
    username: str
    email: EmailStr


# Для сценария без пароля (импорт пользователй)
class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime
    active_resume_id: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )  # для работы с SQLAlchemy моделей


class UserRegisterSchema(UserBase):
    password: constr(min_length=8, max_length=128)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
