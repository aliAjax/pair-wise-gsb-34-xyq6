from sqlalchemy.orm import Session

from src.constants.log_templates import LOG_TEMPLATES
from src.models.hazard_ticket import AuditLog
from src.repositories.hazard_ticket_repository import AuditLogRepository


def render_template(entity: str, event: str, **kwargs) -> str:
    for entry in LOG_TEMPLATES.get(entity, []):
        action, template = entry.split("|", 1)
        if action == event:
            try:
                return template.format(**kwargs)
            except KeyError:
                return template
    return event


def write_audit_log(db: Session, actor: str, entity: str, event: str, target_type: str, target_id, **kwargs):
    """所有写操作统一落审计日志；与业务写操作同事务提交。"""
    detail = render_template(entity, event, **kwargs)
    log = AuditLog(actor=actor, action=event, target_type=target_type, target_id=str(target_id), detail=detail)
    return AuditLogRepository(db).add(log)
