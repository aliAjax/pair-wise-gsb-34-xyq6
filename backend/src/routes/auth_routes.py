from fastapi import APIRouter, Depends

from src.controllers.auth_controller import list_audit_logs, login
from src.middlewares.rbac_middleware import allow_roles

router = APIRouter(prefix="/api/auth", tags=["Auth"])
router.post("/login", response_model=None)(login)
router.get(
    "/audit-logs",
    response_model=None,
    dependencies=[Depends(allow_roles("AUDITOR", "SUPERVISOR"))],
)(list_audit_logs)
