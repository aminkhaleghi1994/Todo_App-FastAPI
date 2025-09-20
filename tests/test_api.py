def test_login_response_401(anonymous_client):
    payload = {
        "username": "admin",
        "password": "12345"
    }
    response = anonymous_client.post("/users/login", json=payload)
    assert response.status_code == 401