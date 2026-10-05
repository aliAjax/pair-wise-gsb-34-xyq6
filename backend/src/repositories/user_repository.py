from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.id)))

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def find_by_username(self, username: str) -> User | None:
        return self.session.scalars(select(User).where(User.username == username)).first()
