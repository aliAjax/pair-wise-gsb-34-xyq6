from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.inspection_result import InspectionResult


class ResultConflictError(Exception):
    """同一任务+检查项结果已存在（唯一约束兜底并发）。"""


class InspectionResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self, task_id: int | None = None, device_id: int | None = None):
        query = self.db.query(InspectionResult)
        if task_id is not None:
            query = query.filter(InspectionResult.task_id == task_id)
        if device_id is not None:
            query = query.filter(InspectionResult.device_id == device_id)
        return query.order_by(InspectionResult.task_id.asc(), InspectionResult.id.asc()).all()

    def list_by_task(self, task_id: int):
        return (
            self.db.query(InspectionResult)
            .filter(InspectionResult.task_id == task_id)
            .order_by(InspectionResult.id.asc())
            .all()
        )

    def count_by_task(self, task_id: int) -> int:
        return (
            self.db.query(InspectionResult)
            .filter(InspectionResult.task_id == task_id)
            .count()
        )

    def save(self, result: InspectionResult) -> InspectionResult:
        try:
            self.db.add(result)
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            raise ResultConflictError(str(exc.orig)) from exc
        return result
