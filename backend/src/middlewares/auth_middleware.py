"""JWT 认证中间件：解析 Bearer Token 并把当前用户挂到 request.state.user。"""

from src.constants.error_codes import ERROR_CODES
from src.services.errors import AuthRequiredError
from src.services.security import decode_access_token

PUBLIC_PATHS = {"/health", "/api/auth/login", "/docs", "/openapi.json", "/redoc"}


async def auth_middleware(request, call_next):
    request.state.user = None
    path = request.url.path
    if request.method == "OPTIONS" or path in PUBLIC_PATHS:
        return await call_next(request)

    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise AuthRequiredError()
    payload = decode_access_token(authorization.removeprefix("Bearer ").strip())
    request.state.user = {
        "id": int(payload["uid"]),
        "role": payload["role"],
        "username": payload.get("sub"),
    }
    return await call_next(request)
