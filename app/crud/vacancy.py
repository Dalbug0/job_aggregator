from sqlalchemy.orm import Session
from app.models import Vacancy

def create_vacancy(db: Session, title: str, company: str, location: str, url: str):
    vacancy = Vacancy(title=title, company=company, location=location, url=url)
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy
