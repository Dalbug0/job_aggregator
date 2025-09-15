from apscheduler.schedulers.background import BackgroundScheduler
from app.services.hh_api import fetch_vacancies
from app.crud.vacancy import create_vacancy
from app.database import SessionLocal
from app.schemas.vacancy import VacancyCreate
from app.logger import logger

def job_fetch_vacancies():
    logger.info("Запуск задачи по сбору вакансий...")

    db = SessionLocal()
    try:
        items = fetch_vacancies("Python", area=1002)
        logger.info(f"Получено {len(items)} вакансий")

        for item in items:
            vacancy_data = VacancyCreate(
                title=item["name"],
                company=item["employer"]["name"] if item.get("employer") else "N/A",
                location=item["area"]["name"] if item.get("area") else "N/A",
                url=item["alternate_url"]
            )
            create_vacancy(db, vacancy_data)

        logger.info("Добавление вакансий завершено успешно")

    except Exception as error:
        logger.exception(f"Ошибка при сборе вакансий: {error}")

    finally:
        db.close()
        logger.debug("Соединение с БД закрыто")


def start_scheduler():
    logger.info("🚀 Запуск планировщика задач...")
    scheduler = BackgroundScheduler()
    job_fetch_vacancies()
    scheduler.add_job(job_fetch_vacancies, "interval", minutes=1)
    scheduler.start()
    logger.info("✅ Планировщик задач запущен (интервал: 1 минута)")
