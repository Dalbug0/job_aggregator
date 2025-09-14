from apscheduler.schedulers.background import BackgroundScheduler
from app.services.hh_api import fetch_vacancies
from app.crud.vacancy import create_vacancy
from app.database import SessionLocal

def job_fetch_vacancies():
    db = SessionLocal()
    try:
        items = fetch_vacancies("Python", area=1002)
        for item in items:
            create_vacancy(
                db,
                title=item["name"],
                company=item["employer"]["name"] if item.get("employer") else "N/A",
                location=item["area"]["name"] if item.get("area") else "N/A",
                url=item["alternate_url"]
            )
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_fetch_vacancies, "interval", hours=1)
    scheduler.start()
