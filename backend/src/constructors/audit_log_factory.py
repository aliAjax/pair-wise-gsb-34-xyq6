from src.models.hazard_ticket import AuditLog
from src.types.audit_payload import AuditLogResponse


def build_audit_log_response(log: AuditLog) -> AuditLogResponse:
    return AuditLogResponse(
        id=log.id,
        actor=log.actor,
        action=log.action,
        target_type=log.target_type,
        target_id=log.target_id,
        detail=log.detail,
        created_at=log.created_at.isoformat() if log.created_at else None,
    )


def build_audit_log_list(logs) -> list[AuditLogResponse]:
    return [build_audit_log_response(row) for row in logs]
