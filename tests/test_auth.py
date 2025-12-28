ROUT = "/auth"


# Регистрация пользователей
def test_register_user_success(client):
    registration_data = {
        "username": "testuser_success",
        "email": "test@example.com",
        "password": "password123",
    }
    response = client.post(f"{ROUT}/register", json=registration_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["user_id"], int)
    assert data["user_id"] > 0


def test_register_user_duplicate_email(client):
    registration_data = {
        "username": "testuser_duplicate1",
        "email": "duplicate@example.com",
        "password": "password123",
    }

    response1 = client.post(f"{ROUT}/register", json=registration_data)
    assert response1.status_code == 200

    registration_data["username"] = "testuser_duplicate2"
    response2 = client.post(f"{ROUT}/register", json=registration_data)
    assert response2.status_code == 400


def test_register_user_invalid_password(client):
    registration_data = {
        "username": "testuser_invalid_pass",
        "email": "invalidpass@example.com",
        "password": "123",  # слишком короткий пароль
    }
    response = client.post(f"{ROUT}/register", json=registration_data)
    assert response.status_code == 422  # Validation error


def test_register_user_invalid_email(client):
    """Тест регистрации с невалидным email"""
    registration_data = {
        "username": "testuser_invalid_email",
        "email": "invalid-email",  # невалидный email
        "password": "password123",
    }
    response = client.post(f"{ROUT}/register", json=registration_data)
    assert response.status_code == 422  # Validation error


def test_login_success(client):
    registration_data = {
        "username": "testuser_login_success",
        "email": "login@example.com",
        "password": "password123",
    }
    client.post(f"{ROUT}/register", json=registration_data)

    login_data = {"email": "login@example.com", "password": "password123"}
    response = client.post(f"{ROUT}/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)


def test_login_wrong_password(client):
    registration_data = {
        "username": "testuser_wrong_pass",
        "email": "wrongpass@example.com",
        "password": "password123",
    }
    client.post(f"{ROUT}/register", json=registration_data)

    login_data = {
        "email": "wrongpass@example.com",
        "password": "wrongpassword",
    }
    response = client.post(f"{ROUT}/login", json=login_data)
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123",
    }
    response = client.post(f"{ROUT}/login", json=login_data)
    assert response.status_code == 401


def test_refresh_token_success(client):
    registration_data = {
        "username": "testuser_refresh",
        "email": "refresh@example.com",
        "password": "password123",
    }
    client.post(f"{ROUT}/register", json=registration_data)

    login_data = {"email": "refresh@example.com", "password": "password123"}
    login_response = client.post(f"{ROUT}/login", json=login_data)
    refresh_token = login_response.json()["refresh_token"]

    refresh_data = {"refresh_token": refresh_token}
    response = client.post(f"{ROUT}/refresh", json=refresh_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)


def test_refresh_token_invalid(client):
    """Тест обновления с невалидным токеном"""
    refresh_data = {"refresh_token": "invalid_refresh_token"}
    response = client.post(f"{ROUT}/refresh", json=refresh_data)
    assert response.status_code == 401


def test_refresh_token_missing(client):
    refresh_data = {}
    response = client.post(f"{ROUT}/refresh", json=refresh_data)
    assert response.status_code == 422  # Validation error
