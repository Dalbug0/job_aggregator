import pytest

from app.services.hh_api import fetch_vacancies


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db(client):
    response = client.get("/health/db")
    assert response.status_code in (200, 503)
    if response.status_code == 200:
        assert response.json() == {"db": "ok"}
    else:
        assert response.json()["db"] == "unavailable"


def test_get_vacancies_empty(client):
    response = client.get("/vacancies")
    assert response.status_code == 200
    assert response.json() == []


def test_post_vacancy(client):
    vacancy_data = {
        "title": "Python Developer",
        "company": "Test Company",
        "location": "Moscow",
        "url": "https://example.com/job/1",
    }

    response = client.post("/vacancies", json=vacancy_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Python Developer"
    assert data["company"] == "Test Company"
    assert data["location"] == "Moscow"
    assert "id" in data
    assert "created_at" in data


def test_update_vacancy(client):
    vacancy_data = {
        "title": "Backend Dev",
        "company": "Test",
        "location": "Minsk",
        "url": "https://example.com/job/1",
    }
    response = client.post("/vacancies/", json=vacancy_data)
    vacancy_id = response.json()["id"]

    update_data = {"title": "Senior Backend Dev"}
    response = client.put(f"/vacancies/{vacancy_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Senior Backend Dev"


def test_delete_vacancy(client):
    vacancy_data = {
        "title": "ToDelete",
        "company": "Test",
        "location": "Minsk",
        "url": "https://example.com/job/1",
    }
    response = client.post("/vacancies/", json=vacancy_data)
    vacancy_id = response.json()["id"]

    response = client.delete(f"/vacancies/{vacancy_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_fetch_vacancies_hh_api(monkeypatch):
    fake_data = {
        "items": [
            {"id": "1", "name": "Python Developer"},
            {"id": "2", "name": "Backend Engineer"},
        ]
    }

    class DummyResponse:
        def __init__(self, json_data, status_code=200):
            self._json = json_data
            self.status_code = status_code

        def json(self):
            return self._json

        def raise_for_status(self):
            pass

    def fake_get(url, params=None, **kwargs):
        return DummyResponse(fake_data)

    monkeypatch.setattr("app.services.hh_api.requests.get", fake_get)

    result = fetch_vacancies("python")
    assert len(result) == 2
    assert result[0]["name"] == "Python Developer"
    assert result[1]["name"] == "Backend Engineer"
