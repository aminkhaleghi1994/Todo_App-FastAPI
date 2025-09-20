def test_login_invalid_data_response_401(anonymous_client):
    payload = {
        "username": "admin",
        "password": "12345"
    }
    response = anonymous_client.post("/users/login", json=payload)
    assert response.status_code == 401

    payload = {
        "username": "test_user",
        "password": "1234"
    }
    response = anonymous_client.post("/users/login", json=payload)
    assert response.status_code == 401

def test_login_response_200(anonymous_client):
    payload = {
        "username": "test_user",
        "password": "123"
    }
    response = anonymous_client.post("/users/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_register_response_201(anonymous_client):
    payload = {
        "username": "admin",
        "password": "12345",
        "password_confirmation": "12345"
    }
    response = anonymous_client.post("/users/register", json=payload)
    assert response.status_code == 201
