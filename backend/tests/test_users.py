from uuid import UUID

from app.extensions import db
from app.users.models import User


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


def test_regular_user_cannot_list_users(client, auth_headers):
    response = client.get(
        "/api/v1/users",
        headers=auth_headers,
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "forbidden"


def test_admin_can_list_users(client, admin_headers):
    response = client.get(
        "/api/v1/users",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["role"] == "admin"


def test_user_can_get_own_profile(client, user, auth_headers):
    response = client.get(
        f"/api/v1/users/{user['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == user["id"]
    assert data["email"] == user["email"]


def test_user_cannot_get_another_profile(client, auth_headers):
    other_user_response = client.post(
        "/api/v1/users",
        json={
            "name": "Another User",
            "email": "another@example.com",
            "password": "password123",
        },
    )

    assert other_user_response.status_code == 201

    other_user = other_user_response.get_json()

    response = client.get(
        f"/api/v1/users/{other_user['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "forbidden"


def test_user_cannot_update_another_profile(client, auth_headers):
    other_user_response = client.post(
        "/api/v1/users",
        json={
            "name": "Another User",
            "email": "another@example.com",
            "password": "password123",
        },
    )

    assert other_user_response.status_code == 201

    other_user = other_user_response.get_json()

    response = client.patch(
        f"/api/v1/users/{other_user['id']}",
        headers=auth_headers,
        json={
            "name": "Hacked Name",
        },
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "forbidden"

    saved_user = db.session.get(User, UUID(other_user["id"]))

    assert saved_user.name == "Another User"


def test_user_can_update_own_profile(client, user, auth_headers):
    response = client.patch(
        f"/api/v1/users/{user['id']}",
        headers=auth_headers,
        json={
            "name": "Updated User",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == user["id"]
    assert data["name"] == "Updated User"
    assert data["email"] == user["email"]

    saved_user = db.session.get(User, UUID(user["id"]))

    assert saved_user.name == "Updated User"


def test_regular_user_cannot_delete_user(client, user, auth_headers):
    response = client.delete(
        f"/api/v1/users/{user['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 403

    saved_user = db.session.get(User, UUID(user["id"]))

    assert saved_user is not None
