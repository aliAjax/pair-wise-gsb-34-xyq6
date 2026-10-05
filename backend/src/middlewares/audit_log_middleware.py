from starlette.middleware.base import BaseHTTPMiddleware

# 写操作的结构化访问日志（审计明细仍由 audit_service 落库）。
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.method in WRITE_METHODS and request.url.path.startswith("/api/"):
            actor = "anonymous"
            user = getattr(request.state, "user", None)
            if user:
                actor = f"{user.get('username', user['id'])}({user['role']})"
            print(
                f"[audit] {request.method} {request.url.path} -> {response.status_code} by {actor}",
                flush=True,
            )
        return response


async def audit_log_middleware(request, call_next):
    return await AuditLogMiddleware.__new__(AuditLogMiddleware).dispatch(request, call_next)
