from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.constants.error_codes import ERROR_CODES
from src.services.errors import ServiceError


def to_error_payload(exc):
    return {"code": getattr(exc, "code", "INTERNAL_ERROR"), "message": str(exc)}


async def service_error_handler(request: Request, exc: ServiceError):
    # Service 层抛出的业务异常：统一错误码响应。
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Controller 层的 Pydantic 入参校验异常单独包装。
    first = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(part) for part in first.get("loc", []) if part != "body")
    message = f"字段 {loc or '请求体'} 格式不正确" if loc else "提交内容缺失或格式不正确"
    return JSONResponse(
        status_code=422,
        content={"code": ERROR_CODES["VALIDATION_FAILED"], "message": message, "detail": exc.errors()},
    )


async def unhandled_error_handler(request: Request, exc: Exception):
    # 兜底：禁止把异常堆栈直接暴露给前端。
    print(f"[error] unhandled: {exc!r}", flush=True)
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "服务内部错误，请联系管理员"},
    )
