from sqlalchemy.orm import Session

from src.constructors.user_factory import build_user_response
from src.db.session import SessionLocal
from src.repositories.user_repository import UserRepository
from src.services.audit_service import write_audit_log
from src.services.errors import AuthError
from src.utils.security import create_access_token, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def login(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise AuthError("AUTH_REQUIRED", "用户名或密码不正确")
        token = create_access_token(user.id, user.role, username=user.username)
        write_audit_log(
            self.db,
            actor=user.username,
            entity="Auth",
            event="Auth.login",
            target_type="User",
            target_id=user.id,
            user_id=user.id,
        )
        self.db.commit()
        return {"access_token": token, "token_type": "bearer", "user": build_user_response(user)}

    def me(self, user_id: int):
        user = self.user_repo.get(user_id)
        if not user:
            raise AuthError("TOKEN_INVALID", "用户不存在")
        return build_user_response(user)

    def list_users(self):
        return self.user_repo.find_all()


def build_auth_service() -> AuthService:
    # 仅供非依赖注入场景使用。
    return AuthService(SessionLocal())
