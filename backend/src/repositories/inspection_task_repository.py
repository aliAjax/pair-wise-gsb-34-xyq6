from sqlalchemy.orm import Session

from src.models.inspection_task import ChecklistItem, ChecklistTemplate, InspectionTask


class InspectionTaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self, building_id: int | None = None, status: str | None = None):
        query = self.db.query(InspectionTask)
        if building_id is not None:
            query = query.filter(InspectionTask.building_id == building_id)
        if status is not None:
            query = query.filter(InspectionTask.status == status)
        return query.order_by(InspectionTask.plan_date.desc(), InspectionTask.id.desc()).all()

    def get(self, task_id: int) -> InspectionTask | None:
        return self.db.get(InspectionTask, task_id)

    def save(self, task: InspectionTask) -> InspectionTask:
        self.db.add(task)
        self.db.flush()
        return task

    def list_checklist_items(self, task_id: int):
        return (
            self.db.query(ChecklistItem)
            .filter(ChecklistItem.task_id == task_id)
            .order_by(ChecklistItem.id.asc())
            .all()
        )

    def active_checklist_items(self, task_id: int):
        return (
            self.db.query(ChecklistItem)
            .filter(ChecklistItem.task_id == task_id, ChecklistItem.deprecated.is_(False))
            .order_by(ChecklistItem.id.asc())
            .all()
        )

    def get_checklist_item(self, task_id: int, item_code: str) -> ChecklistItem | None:
        return (
            self.db.query(ChecklistItem)
            .filter(ChecklistItem.task_id == task_id, ChecklistItem.item_code == item_code)
            .one_or_none()
        )

    def add_checklist_items(self, items):
        self.db.add_all(items)
        self.db.flush()

    def mark_deprecated(self, task_id: int, item_codes):
        if not item_codes:
            return
        (
            self.db.query(ChecklistItem)
            .filter(ChecklistItem.task_id == task_id, ChecklistItem.item_code.in_(item_codes))
            .update({ChecklistItem.deprecated: True}, synchronize_session=False)
        )
        self.db.flush()

    def latest_template_version(self, task_type: str) -> str | None:
        row = (
            self.db.query(ChecklistTemplate.version)
            .filter(ChecklistTemplate.task_type == task_type)
            .distinct()
            .all()
        )
        versions = sorted(v for (v,) in row)
        return versions[-1] if versions else None

    def list_template(self, task_type: str, version: str):
        return (
            self.db.query(ChecklistTemplate)
            .filter(ChecklistTemplate.task_type == task_type, ChecklistTemplate.version == version)
            .order_by(ChecklistTemplate.id.asc())
            .all()
        )

    def add_template_items(self, items):
        self.db.add_all(items)
        self.db.flush()
