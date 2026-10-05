"""登录认证：校验种子用户并签发 JWT。"""

from sqlalchemy.orm import Session

from src.constructors.audit_log_factory import create_audit_log_dto
from src.models.user import LoginResponse
from src.repositories.audit_log_repository import AuditLogRepository
from src.repositories.user_repository import UserRepository
from src.services.audit_service import write_audit
from src.services.errors import BusinessError
from src.services.security import create_access_token


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def login(self, username: str, password: str) -> dict:
        user = self.user_repo.find_by_username(username)
        # 演示环境明文口令；生产应由哈希校验
        if user is None or user.password != password:
            raise BusinessError("INVALID_CREDENTIALS", status_code=401)
        token = create_access_token(user.id, user.role)
        write_audit(
            self.session,
            {"id": user.id, "username": user.username, "role": user.role},
            "Auth.login",
            "User",
            user.id,
            f"用户登录：{user.name}",
        )
        self.session.commit()
        return LoginResponse(
            access_token=token,
            user={"id": user.id, "username": user.username, "name": user.name, "role": user.role},
        ).model_dump(mode="json")

    def list_audit_logs(self, limit: int = 200) -> list[dict]:
        logs = AuditLogRepository(self.session).find_all(limit=limit)
        return [create_audit_log_dto(log) for log in logs]
