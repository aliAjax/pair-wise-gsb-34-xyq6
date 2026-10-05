from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import AuditLog


class AuditLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self, limit: int = 200) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
        return list(self.session.scalars(stmt))

    def add(self, log: AuditLog) -> AuditLog:
        self.session.add(log)
        self.session.flush()
        return log
