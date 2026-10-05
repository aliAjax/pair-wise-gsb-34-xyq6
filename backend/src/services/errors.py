"""业务异常：service 抛出、controller/全局处理器分别包装。"""

from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES


class BusinessError(Exception):
    def __init__(self, code: str, message: str | None = None, status_code: int = 400):
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, code)
        self.status_code = status_code
        super().__init__(self.message)

    def with_detail(self, **kwargs) -> "BusinessError":
        try:
            self.message = self.message.format(**kwargs)
        except (KeyError, IndexError):
            pass
        return self


class AuthRequiredError(BusinessError):
    def __init__(self):
        super().__init__(ERROR_CODES["AUTH_REQUIRED"], status_code=401)


class InvalidTokenError(BusinessError):
    def __init__(self):
        super().__init__(ERROR_CODES["INVALID_TOKEN"], status_code=401)


class RbacDeniedError(BusinessError):
    def __init__(self):
        super().__init__(ERROR_CODES["RBAC_DENIED"], status_code=403)


class NotFoundError(BusinessError):
    def __init__(self, code: str = "NOT_FOUND"):
        super().__init__(ERROR_CODES[code], status_code=404)


class ConflictError(BusinessError):
    def __init__(self, code: str, **detail):
        message = ERROR_MESSAGES[code].format(**detail) if detail else None
        super().__init__(ERROR_CODES[code], message=message, status_code=409)
