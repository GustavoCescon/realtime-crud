def test_login_with_valid_credentials(client, user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "access_token" in data
    assert data["access_token"]


def test_login_with_invalid_password(client, user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "invalid_credentials"


def test_me_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_valid_token(client, user):
    login_response = client.post(
        "/api/v1/auth/login", json={"email": user["email"], "password": "password123"}
    )

    assert login_response.status_code == 200

    access_token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == user["id"]
    assert data["email"] == user["email"]
    assert data["name"] == user["name"]
