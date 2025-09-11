from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional

class VacancyBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    url: Optional[HttpUrl] = None

class VacancyCreate(VacancyBase):
    pass

class VacancyRead(VacancyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # для работы с SQLAlchemy моделей
