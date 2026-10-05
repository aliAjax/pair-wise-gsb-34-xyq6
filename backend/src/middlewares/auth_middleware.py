from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.security import decode_access_token

# 免鉴权路径：健康检查、登录、文档。
PUBLIC_PATHS = {"/health", "/api/auth/login", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if path in PUBLIC_PATHS or path.startswith("/docs"):
            request.state.user = None
            return await call_next(request)

        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"code": "AUTH_REQUIRED", "message": "缺少登录令牌，请先登录"},
            )
        token = authorization.removeprefix("Bearer ").strip()
        try:
            payload = decode_access_token(token)
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"code": "TOKEN_INVALID", "message": "登录令牌无效或已过期，请重新登录"},
            )
        request.state.user = {"id": int(payload["sub"]), "role": payload["role"], "username": payload.get("username", "")}
        return await call_next(request)


async def auth_middleware(request, call_next):
    # 兼容 main.py 中的函数式注册方式。
    return await AuthMiddleware.__new__(AuthMiddleware).dispatch(request, call_next)
