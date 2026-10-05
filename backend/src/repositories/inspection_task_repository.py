from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.entities import InspectionTask, TaskChecklistItem


class InspectionTaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self, building_id: int | None = None, status: str | None = None) -> list[InspectionTask]:
        stmt = (
            select(InspectionTask)
            .options(selectinload(InspectionTask.items), selectinload(InspectionTask.results))
            .order_by(InspectionTask.plan_date.desc(), InspectionTask.id.desc())
        )
        if building_id is not None:
            stmt = stmt.where(InspectionTask.building_id == building_id)
        if status is not None:
            stmt = stmt.where(InspectionTask.status == status)
        return list(self.session.scalars(stmt))

    def get(self, task_id: int) -> InspectionTask | None:
        stmt = (
            select(InspectionTask)
            .where(InspectionTask.id == task_id)
            .options(selectinload(InspectionTask.items), selectinload(InspectionTask.results))
        )
        return self.session.scalars(stmt).first()

    def add(self, task: InspectionTask) -> InspectionTask:
        self.session.add(task)
        self.session.flush()
        return task

    def list_items(self, task_id: int) -> list[TaskChecklistItem]:
        stmt = (
            select(TaskChecklistItem)
            .where(TaskChecklistItem.task_id == task_id)
            .order_by(TaskChecklistItem.device_id, TaskChecklistItem.id)
        )
        return list(self.session.scalars(stmt))
