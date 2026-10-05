from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.constants.roles import ROLE_AUDITOR, ROLE_SUPERVISOR
from src.constructors.audit_log_factory import build_audit_log_list
from src.db.session import get_db
from src.middlewares.rbac_middleware import require_roles
from src.services.audit_log_service import AuditLogService

router = APIRouter()


@router.get("")
def list_audit_logs(
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_AUDITOR, ROLE_SUPERVISOR)),
):
    service = AuditLogService(db)
    return build_audit_log_list(service.list_recent(limit=limit))
