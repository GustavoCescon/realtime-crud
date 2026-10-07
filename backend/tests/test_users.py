def test_create_user(client):
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_create_user_with_duplicate_email(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    }

    first_response = client.post(
        "/api/v1/users",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/users",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    data = second_response.get_json()

    assert data["error"] == "email_already_exists"
