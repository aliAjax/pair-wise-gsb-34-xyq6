"""访问日志中间件：记录每个请求的方法、路径与操作者（业务审计落库在 service 层）。"""


async def audit_log_middleware(request, call_next):
    user = getattr(request.state, "user", None)
    actor = user["role"] if user else "anonymous"
    print(f"[access] {request.method} {request.url.path} actor={actor}")
    response = await call_next(request)
    print(f"[access] {request.method} {request.url.path} -> {response.status_code}")
    return response
