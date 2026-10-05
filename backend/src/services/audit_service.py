"""业务审计日志：所有写操作在 service 层同事务落库。"""

from sqlalchemy.orm import Session

from src.models.entities import AuditLog


def write_audit(
    session: Session,
    actor: dict | None,
    action: str,
    target_type: str = "",
    target_id: str | int = "",
    detail: str = "",
) -> AuditLog:
    log = AuditLog(
        actor_id=actor.get("id") if actor else None,
        actor_name=actor.get("username", "") if actor else "",
        actor_role=actor.get("role", "") if actor else "",
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        detail=detail,
    )
    session.add(log)
    session.flush()
    return log
