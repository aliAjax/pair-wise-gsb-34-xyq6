"""全局错误处理：业务异常/请求校验异常统一包装成 {code,message}。"""

from fastapi import Request
from fastapi.responses import JSONResponse

from src.constants.error_codes import ERROR_CODES
from src.services.errors import BusinessError


def to_error_payload(exc) -> dict:
    return {"code": getattr(exc, "code", ERROR_CODES["INTERNAL_ERROR"]), "message": str(exc)}


async def error_guard_middleware(request: Request, call_next):
    """中间件层兜底：认证等中间件抛出的业务异常也返回统一错误体。"""
    try:
        return await call_next(request)
    except BusinessError as exc:
        return JSONResponse(
            status_code=getattr(exc, "status_code", 400),
            content=to_error_payload(exc),
        )
    except Exception as exc:  # noqa: BLE001
        import os
        import traceback

        if os.getenv("DEBUG_ERRORS"):
            traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "code": ERROR_CODES["INTERNAL_ERROR"],
                "message": "服务繁忙，请稍后再试",
            },
        )


async def business_error_handler(request: Request, exc) -> JSONResponse:
    # controller/service 抛出的业务异常各自携带错误码与 HTTP 状态
    return JSONResponse(
        status_code=getattr(exc, "status_code", 400),
        content=to_error_payload(exc),
    )


async def validation_error_handler(request: Request, exc) -> JSONResponse:
    # Pydantic 入参校验错误包装为统一 VALIDATION_FAILED
    detail = getattr(exc, "errors", lambda: [])()
    return JSONResponse(
        status_code=422,
        content={
            "code": ERROR_CODES["VALIDATION_FAILED"],
            "message": "表单字段缺失或格式错误",
            "detail": detail,
        },
    )


async def unhandled_error_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"code": ERROR_CODES["INTERNAL_ERROR"], "message": "服务繁忙，请稍后再试"},
    )
