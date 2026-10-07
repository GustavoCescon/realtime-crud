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
