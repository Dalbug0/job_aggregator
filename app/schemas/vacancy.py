from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, HttpUrl

from app.examples import vacancy


class VacancyBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    url: Optional[HttpUrl] = None
    salary: Optional[Dict] = None
    source: Optional[str] = "hh.ru"  # None

    class Config:
        json_schema_extra = {"example": vacancy.vacancy_example}


class VacancyCreate(VacancyBase):
    pass


class VacancyRead(VacancyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # для работы с SQLAlchemy моделей
        json_schema_extra = {"example": vacancy.vacancy_read_example}
        json_schema_extra = {"example": vacancy.vacancy_read_example}


class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[HttpUrl] = None
    salary: Optional[Dict] = None
    source: Optional[str] = None


class VacancyDelete(BaseModel):
    ok: bool
