from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from pydantic import ValidationError

from app.users.repository import UserRepository
from app.users.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
)
from app.users.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)
from app.common.decorators import (
    owner_or_roles_required,
    roles_required,
)

users_bp = Blueprint(
    "users",
    __name__,
)

repository = UserRepository()
service = UserService(repository)

def serialize_user(user):
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }

@users_bp.post("")
def create_user():

    data = CreateUserRequest.model_validate(
        request.get_json()
    )

    user = service.create(data)

    return jsonify(
        serialize_user(user)
    ), 201

@users_bp.patch("/<uuid:user_id>")
@jwt_required()
@owner_or_roles_required("admin")
def update_user(user_id: UUID):

    data = UpdateUserRequest.model_validate(
        request.get_json()
    )

    user = service.update(
        user_id,
        data,
    )

    return jsonify(
        serialize_user(user)
    )

@users_bp.get("")
@jwt_required()
@roles_required("admin")
def get_users():
    users = service.get_all()

    return jsonify([
        serialize_user(user)
        for user in users
    ])


@users_bp.get("/<uuid:user_id>")
@jwt_required()
@owner_or_roles_required("admin")
def get_user(user_id: UUID):
    user = service.get_by_id(user_id)

    return jsonify(serialize_user(user))

@users_bp.delete("/<uuid:user_id>")
@jwt_required()
@roles_required("admin")
def delete_user(user_id: UUID):
    service.delete(user_id)

    return "", 204
