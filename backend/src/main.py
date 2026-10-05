from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.middlewares.audit_log_middleware import audit_log_middleware
from src.middlewares.auth_middleware import auth_middleware
from src.middlewares.error_handler_middleware import (
    business_error_handler,
    error_guard_middleware,
    unhandled_error_handler,
    validation_error_handler,
)
from src.middlewares.rate_limit_middleware import rate_limit_middleware
from src.routes.auth_routes import router as auth_router
from src.routes.building_routes import router as building_router
from src.routes.fire_device_routes import router as fire_device_router
from src.routes.hazard_ticket_routes import router as hazard_ticket_router
from src.routes.inspection_result_routes import router as inspection_result_router
from src.routes.inspection_task_routes import router as inspection_task_router
from src.routes.stats_routes import router as stats_router
from src.seed import seed_database
from src.services.errors import BusinessError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 建表并幂等写入本地种子数据
    seed_database()
    yield


app = FastAPI(title="消防设施巡检维保平台", lifespan=lifespan)

# Starlette 后添加的中间件更靠外；最终外 -> 内顺序：
# 访问日志 -> 错误兜底 -> 认证 -> 限流 -> 路由
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(auth_middleware)
app.middleware("http")(error_guard_middleware)
app.middleware("http")(audit_log_middleware)

# 业务异常与参数校验异常分别包装，禁止全局吞掉全部异常细节
app.add_exception_handler(BusinessError, business_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


@app.get("/health")
def health():
    return {"status": "ok", "service": "fire-inspect"}


app.include_router(auth_router)
app.include_router(building_router)
app.include_router(fire_device_router)
app.include_router(inspection_task_router)
app.include_router(inspection_result_router)
app.include_router(hazard_ticket_router)
app.include_router(stats_router)
