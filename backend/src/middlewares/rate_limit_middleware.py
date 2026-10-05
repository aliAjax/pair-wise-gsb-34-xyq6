"""简单固定窗口限流中间件：登录接口单独更严格的配额。"""

import time
from collections import defaultdict

from starlette.responses import JSONResponse

from src.config.settings import settings
from src.constants.error_codes import ERROR_CODES

_WINDOW_SECONDS = 60
_hits: dict[str, list[float]] = defaultdict(list)


def _client_key(request) -> str:
    user = getattr(request.state, "user", None)
    if user:
        return f"user:{user['id']}"
    return f"ip:{request.client.host if request.client else 'unknown'}"


async def rate_limit_middleware(request, call_next):
    if request.method == "GET" or request.url.path in {"/health", "/docs", "/openapi.json"}:
        return await call_next(request)

    limit = (
        settings.LOGIN_RATE_LIMIT_PER_MINUTE
        if request.url.path == "/api/auth/login"
        else settings.RATE_LIMIT_PER_MINUTE
    )
    now = time.monotonic()
    key = _client_key(request)
    bucket = [ts for ts in _hits[key] if now - ts < _WINDOW_SECONDS]
    if len(bucket) >= limit:
        return JSONResponse(
            status_code=429,
            content={
                "code": ERROR_CODES["RATE_LIMITED"],
                "message": "请求过于频繁，请稍后再试",
            },
        )
    bucket.append(now)
    _hits[key] = bucket
    return await call_next(request)
