from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from app.auth.schemas import LoginRequest
from app.auth.service import AuthService
from app.users.repository import UserRepository


auth_bp = Blueprint("auth", __name__)

repository = UserRepository()
service = AuthService(repository)


@auth_bp.post("/login")
def login():
    data = LoginRequest.model_validate(request.get_json())

    user = service.authenticate(
        email=data.email,
        password=data.password,
    )

    access_token = service.create_access_token(user)
    refresh_token = service.create_refresh_token(user)

    response = jsonify({
        "access_token": access_token,
    })

    set_refresh_cookies(
        response,
        refresh_token,
    )

    return response

@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = service.get_authenticated_user(user_id)

    return jsonify({
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    })

@auth_bp.post("/refresh")
@jwt_required(refresh=True, locations=["cookies"])
def refresh():
    user_id = get_jwt_identity()

    user = service.get_authenticated_user(user_id)

    access_token = service.create_access_token(user)

    return jsonify({
        "access_token": access_token,
    })

@auth_bp.post("/logout")
def logout():
    response = jsonify({
        "message": "logged_out",
    })

    unset_jwt_cookies(response)

    return response
