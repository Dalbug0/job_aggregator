from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserRegisterResponse(BaseModel):
    status: str
    user_id: int


class TelegramUserRegisterResponse(BaseModel):
    status: str
    user_id: int
    telegram_id: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
