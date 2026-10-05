from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES


class ServiceError(Exception):
    """Service 层统一业务异常：携带错误码，默认 HTTP 400。"""

    def __init__(self, code: str, message: str | None = None, status_code: int = 400):
        self.code = code if code in ERROR_CODES else "INTERNAL_ERROR"
        self.message = message or ERROR_MESSAGES.get(self.code, code)
        self.status_code = status_code
        super().__init__(self.message)


class AuthError(ServiceError):
    def __init__(self, code: str = "AUTH_REQUIRED", message: str | None = None):
        super().__init__(code, message, status_code=401)


class RbacError(ServiceError):
    def __init__(self, message: str | None = None):
        super().__init__("RBAC_DENIED", message, status_code=403)


class NotFoundError(ServiceError):
    def __init__(self, message: str | None = None):
        super().__init__("NOT_FOUND", message, status_code=404)


class ConflictError(ServiceError):
    def __init__(self, code: str = "INVALID_STATE", message: str | None = None):
        super().__init__(code, message, status_code=409)
