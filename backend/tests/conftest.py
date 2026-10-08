from uuid import UUID

import pytest
from app import create_app
from app.extensions import db
from app.users.models import User


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(client):
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    return response.get_json()


@pytest.fixture()
def auth_headers(client, user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "password123",
        },
    )

    assert response.status_code == 200

    access_token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture()
def admin_headers(client, user, app):
    with app.app_context():
        admin = db.session.get(User, UUID(user["id"]))

        admin.role = "admin"
        db.session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "password123",
        },
    )

    assert response.status_code == 200

    access_token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }
