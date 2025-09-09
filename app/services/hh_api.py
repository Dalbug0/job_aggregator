import requests

BASE_URL = "https://api.hh.ru/vacancies"

def fetch_vacancies(keyword: str, area: int = 1002, per_page: int = 10):
    params = {
        "text": keyword,
        "area": area,
        "per_page": per_page
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("items", [])
