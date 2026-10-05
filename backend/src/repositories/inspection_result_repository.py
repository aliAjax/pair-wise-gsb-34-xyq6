from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import InspectionResult


class InspectionResultRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self, task_id: int | None = None, device_id: int | None = None) -> list[InspectionResult]:
        stmt = select(InspectionResult).order_by(InspectionResult.id.desc())
        if task_id is not None:
            stmt = stmt.where(InspectionResult.task_id == task_id)
        if device_id is not None:
            stmt = stmt.where(InspectionResult.device_id == device_id)
        return list(self.session.scalars(stmt))

    def find_by_task_item(self, task_id: int, item_code: str) -> InspectionResult | None:
        stmt = select(InspectionResult).where(
            InspectionResult.task_id == task_id,
            InspectionResult.item_code == item_code,
        )
        return self.session.scalars(stmt).first()

    def add(self, result: InspectionResult) -> InspectionResult:
        self.session.add(result)
        self.session.flush()
        return result
