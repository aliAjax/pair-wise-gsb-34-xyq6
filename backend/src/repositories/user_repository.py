from sqlalchemy.orm import Session

from src.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self):
        return self.db.query(User).order_by(User.id.asc()).all()

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).one_or_none()
