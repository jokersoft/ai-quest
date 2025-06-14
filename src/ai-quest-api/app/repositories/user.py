import logging

from app.entities.user import User

_LOGGER = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def add(self, user: User) -> User:
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        _LOGGER.info(f"Inserted a new user: {user.get_id()}")

        return user

    def get(self, user_id_bytes: bytes) -> User:
        return self.db_session.query(User).filter(User.id == user_id_bytes).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db_session.query(User).filter(User.email == email).first()
