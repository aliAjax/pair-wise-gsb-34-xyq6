from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.session import get_session
from src.middlewares.rbac_middleware import current_user
from src.models.user import LoginPayload
from src.services.auth_service import AuthService


def login(payload: LoginPayload, session: Session = Depends(get_session)):
    return AuthService(session).login(payload.username, payload.password)


def list_audit_logs(
    session: Session = Depends(get_session),
    actor: dict = Depends(current_user),
):
    # 角色过滤在路由层限定为审计员/主管
    return AuthService(session).list_audit_logs()
