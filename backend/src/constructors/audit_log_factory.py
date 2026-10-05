"""操作日志响应构造器。"""

from src.constants.log_templates import LOG_LABELS
from src.models.entities import AuditLog


def create_audit_log_dto(log: AuditLog) -> dict:
    return {
        "id": log.id,
        "actor_id": log.actor_id,
        "actor_name": log.actor_name,
        "actor_role": log.actor_role,
        "action": log.action,
        "action_label": LOG_LABELS.get(log.action, log.action),
        "target_type": log.target_type,
        "target_id": log.target_id,
        "detail": log.detail,
        "created_at": log.created_at,
    }
