from sqlalchemy.orm import Session
from app.models import Vacancy
from app.schemas.vacancy import VacancyCreate

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
