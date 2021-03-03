import pytest


def test_success_auth(test_app):
    login, password = 'test_login', 'test_password'
    response = test_app.post("/auth/registration", json={
        "login": login, "password": password
    })
    assert response.status_code == 200

    response = test_app.post("/auth/login", json={
        "login": login, "password": password
    })
    assert response.status_code == 200
    token = response.json()["token"]
    assert isinstance(token, str)

    response = test_app.get("/auth/check", headers={
        "Authorization": "Bearer " + token
    })
    assert response.status_code == 200
    assert response.json()["login"] == login
