from sqlalchemy.orm import Session
from app.models import Vacancy
from app.schemas.vacancy import VacancyCreate, VacancyUpdate
from fastapi import HTTPException

def create_vacancy(db: Session, vacancy: VacancyCreate) -> Vacancy:
    # Приводим HttpUrl (Pydantic) к str, чтобы psycopg2/SQLAlchemy могли использовать его в SQL-запросах.
    # Без этого при передаче HttpUrl напрямую возникнет ошибка:
    # psycopg2.ProgrammingError: can't adapt type 'HttpUrl'
    url_value = str(vacancy.url) if vacancy.url is not None else None

    if url_value is not None:
        existing = db.query(Vacancy).filter(Vacancy.url == url_value).first()
        if existing:
            return existing

    db_vacancy = Vacancy(**vacancy.model_dump(mode="json"))
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy


def get_vacancies(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Vacancy).offset(skip).limit(limit).all()


def update_vacancy(db: Session, vacancy_id: int, vacancy: VacancyUpdate):
    db_vacancy = db.query(Vacancy).get(vacancy_id)
    if not db_vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    for key, value in vacancy.model_dump(exclude_unset=True).items():
        setattr(db_vacancy, key, value)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy


def delete_vacancy(db: Session, vacancy_id: int):
    db_vacancy = db.query(Vacancy).get(vacancy_id)
    if not db_vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    db.delete(db_vacancy)
    db.commit()
    return {"ok": True}