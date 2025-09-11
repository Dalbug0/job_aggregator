from sqlalchemy.orm import Session
from app.models import Vacancy
from app.schemas.vacancy import VacancyCreate

def create_vacancy(db: Session, vacancy: VacancyCreate) -> Vacancy:
    db_vacancy = Vacancy(**vacancy.model_dump(mode="json"))
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

def get_vacancies(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Vacancy).offset(skip).limit(limit).all()
