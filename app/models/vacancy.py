# app/models/vacancy.py
from sqlalchemy import JSON, Column, DateTime, Integer, String, func

from app.database import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    url = Column(String, nullable=True)
    salary = Column(
        JSON, nullable=True
    )  # хранение диапазона зарплаты как JSON
    source = Column(
        String, nullable=True
    )  # источник вакансии (hh.ru, rabota.by)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
