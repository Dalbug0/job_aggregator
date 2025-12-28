# app/services/vacancy_formatter.py
from app.schemas import VacancyCreate


def format_hh_vacancies(data: dict) -> list[VacancyCreate]:
    return [
        VacancyCreate(
            title=v["name"],
            company=v.get("employer", {}).get("name"),
            location=v.get("area", {}).get("name"),
            url=v["alternate_url"],
            salary=v.get("salary"),
            source="hh.ru",
        )
        for v in data.get("items", [])
    ]
