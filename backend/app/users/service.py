from uuid import UUID

from werkzeug.security import generate_password_hash

from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
)

from app.common.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)

class UserService:

    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    def create(
        self,
        data: CreateUserRequest,
    ) -> User:

        existing_user = self.repository.get_by_email(
            data.email
        )

        if existing_user:
            raise UserAlreadyExistsError()

        user = User(
            name=data.name,
            email=data.email,
            password_hash=generate_password_hash(
                data.password
            ),
        )

        return self.repository.create(user)

    def update(
        self,
        user_id: UUID,
        data: UpdateUserRequest,
    ) -> User:

        user = self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(user, field, value)

        return self.repository.update(user)

    def get_all(self) -> list[User]:
        return self.repository.get_all()

    def get_by_id(self, user_id: UUID) -> User:
        user = self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        return user
