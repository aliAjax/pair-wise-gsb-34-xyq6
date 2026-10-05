from sqlalchemy import Column, Integer, String

from src.db.session import Base


class User(Base):
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    display_name = Column(String(64), nullable=False)
    role = Column(String(32), nullable=False)
    password_hash = Column(String(128), nullable=False)
