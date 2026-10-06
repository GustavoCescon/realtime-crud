from uuid import UUID

from app.extensions import db
from app.users.models import User


class UserRepository:

    def get_by_id(self, user_id: UUID) -> User | None:
        return db.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return User.query.filter_by(email=email).first()

    def create(self, user: User) -> User:
        db.session.add(user)
        db.session.commit()

        return user

    def update(self, user: User) -> User:
        db.session.commit()

        return user

    def get_all(self) -> list[User]:
        return User.query.order_by(User.created_at.desc()).all()
