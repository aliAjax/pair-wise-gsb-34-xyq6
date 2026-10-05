from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.db.session import Base, SessionLocal, engine
from src.middlewares.audit_log_middleware import AuditLogMiddleware
from src.middlewares.auth_middleware import AuthMiddleware
from src.middlewares.error_handler_middleware import (
    service_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from src.middlewares.rate_limit_middleware import RateLimitMiddleware
from src.routes.audit_log_routes import router as audit_log_router
from src.routes.auth_routes import router as auth_router
from src.routes.building_routes import router as building_router
from src.routes.dashboard_routes import router as dashboard_router
from src.routes.fire_device_routes import router as fire_device_router
from src.routes.hazard_ticket_routes import router as hazard_ticket_router
from src.routes.inspection_result_routes import router as inspection_result_router
from src.routes.inspection_task_routes import router as inspection_task_router
from src.seed import seed_database
from src.services.errors import ServiceError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 本地 SQLite 也能直接建表；PostgreSQL 首次启动同样由 SQLAlchemy 建表，init.sql 仅作结构参照。
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title="消防设施巡检维保平台", version="1.0.0", lifespan=lifespan)

# 中间件顺序：限流 -> 鉴权 -> 审计输出。
app.add_middleware(AuditLogMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_exception_handler(ServiceError, service_error_handler)
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
app.include_router(dashboard_router)
app.include_router(audit_log_router)
