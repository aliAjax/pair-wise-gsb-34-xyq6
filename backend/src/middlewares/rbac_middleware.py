"""RBAC：路由依赖工厂 + 便捷断言，供 route/controller/service 多层使用。"""

from fastapi import Depends, Request

from src.constants.user_role import (
    ROLE_AUDITOR,
    ROLE_INSPECTOR,
    ROLE_MAINTAINER,
    ROLE_SUPERVISOR,
)
from src.services.errors import AuthRequiredError, RbacDeniedError


def current_user(request: Request) -> dict:
    user = getattr(request.state, "user", None)
    if not user:
        raise AuthRequiredError()
    return user


def allow_roles(*roles: str):
    """FastAPI 依赖：要求当前用户具备任一角色。"""

    def _checker(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise RbacDeniedError()
        return user

    return _checker


require_inspector = allow_roles(ROLE_INSPECTOR)
require_maintainer = allow_roles(ROLE_MAINTAINER)
require_supervisor = allow_roles(ROLE_SUPERVISOR)
require_auditor = allow_roles(ROLE_AUDITOR)
# 登录后的任意业务角色
require_staff = allow_roles(ROLE_INSPECTOR, ROLE_MAINTAINER, ROLE_SUPERVISOR, ROLE_AUDITOR)


def assert_role(user: dict, *roles: str) -> None:
    """service 层二次防御：controller 之外被复用时仍然鉴权。"""
    if user["role"] not in roles:
        raise RbacDeniedError()
