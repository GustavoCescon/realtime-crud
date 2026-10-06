
from uuid import UUID

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)
from werkzeug.security import check_password_hash

from app.common.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.users.repository import UserRepository
from app.users.models import User


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repository.get_by_email(email)

        if not user:
            raise InvalidCredentialsError()

        if not check_password_hash(user.password_hash, password):
            raise InvalidCredentialsError()

        return user

    def create_access_token(self, user: User) -> str:
        return create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role,
            },
        )

    def create_refresh_token(self, user: User) -> str:
        return create_refresh_token(
            identity=str(user.id),
        )

    def get_authenticated_user(self, user_id: str) -> User:
        user = self.user_repository.get_by_id(UUID(user_id))

        if not user:
            raise UserNotFoundError()

        return user
