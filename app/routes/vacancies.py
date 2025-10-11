from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.vacancy import VacancyRead, VacancyCreate, VacancyUpdate, VacancyDelete
from app.crud.vacancy import create_vacancy, get_vacancies, update_vacancy, delete_vacancy

router = APIRouter()

@router.get("/", response_model=List[VacancyRead])
def list_vacancies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_vacancies(db, skip=skip, limit=limit)

@router.post("/", response_model=VacancyRead)
def add_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db)):
    return create_vacancy(db, vacancy)

@router.put("/{vacancy_id}", response_model=VacancyRead)
def up_vacancy(vacancy_id: int, vacancy: VacancyUpdate, db: Session = Depends(get_db)):
    return update_vacancy(db, vacancy_id, vacancy)

@router.delete("/{vacancy_id}", response_model=VacancyDelete)
def del_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    return delete_vacancy(db, vacancy_id)