from fastapi import Depends, Request

from src.services.errors import RbacError


def current_user(request: Request) -> dict:
    user = getattr(request.state, "user", None)
    if not user:
        from src.services.errors import AuthError

        raise AuthError()
    return user


def require_roles(*roles):
    """路由依赖工厂：只允许指定角色访问，其余角色 403。"""

    def checker(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise RbacError(f"当前角色无权执行该操作，需要角色：{'/'.join(roles)}")
        return user

    return checker


def allow_roles(*roles):
    # 保留旧名称的包装，供 controller 显式调用。
    return require_roles(*roles)
