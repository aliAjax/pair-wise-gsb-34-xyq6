from sqlalchemy.orm import Session

from src.repositories.hazard_ticket_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session):
        self.repo = AuditLogRepository(db)

    def list_recent(self, limit: int = 100):
        return self.repo.list_recent(limit=limit)
