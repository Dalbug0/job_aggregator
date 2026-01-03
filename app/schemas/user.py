from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, constr


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None  # Сделаем email опциональным для TelegramUser


# Для сценария без пароля (импорт пользователй)
class UserCreate(UserBase):
    email: EmailStr  # Но для создания обычного пользователя email обязателен
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


class TelegramUserRead(BaseModel):
    id: int
    username: str
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    active_resume_id: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


class TelegramUserRegisterSchema(BaseModel):
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )  # для работы с SQLAlchemy моделей