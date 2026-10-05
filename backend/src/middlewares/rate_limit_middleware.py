import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import RATE_LIMIT_PER_MINUTE


class RateLimitMiddleware(BaseHTTPMiddleware):
    """滑动窗口限流：按客户端 IP 统计，每分钟超过阈值返回 429。"""

    def __init__(self, app, limit: int = RATE_LIMIT_PER_MINUTE):
        super().__init__(app)
        self.limit = limit
        self.window = 60
        self.buckets: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self.buckets[client_ip]
        while bucket and now - bucket[0] > self.window:
            bucket.popleft()
        if len(bucket) >= self.limit:
            from starlette.responses import JSONResponse

            return JSONResponse(
                status_code=429,
                content={"code": "RATE_LIMITED", "message": "请求过于频繁，请稍后再试"},
            )
        bucket.append(now)
        return await call_next(request)
