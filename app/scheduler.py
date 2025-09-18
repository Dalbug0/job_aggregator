from apscheduler import schedulers
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.hh_api import fetch_vacancies
from app.crud.vacancy import create_vacancy
from app.database import SessionLocal
from app.schemas.vacancy import VacancyCreate
from app.logger import logger
from datetime import datetime

scheduler = BackgroundScheduler()

def job_fetch_vacancies():
    db = SessionLocal()
    try:
        items = fetch_vacancies("Python", area=1002)

        for item in items:
            vacancy_data = VacancyCreate(
                title=item["name"],
                company=item["employer"]["name"] if item.get("employer") else "N/A",
                location=item["area"]["name"] if item.get("area") else "N/A",
                url=item["alternate_url"]
            )
            create_vacancy(db, vacancy_data)


    except Exception as error:
        logger.exception(f"Ошибка при сборе вакансий: {error}")

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(job_fetch_vacancies, "interval", minutes=60, next_run_time=datetime.now(), misfire_grace_time=30)
    scheduler.start()

def fin_scheduler():
    scheduler.shutdown();


