from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChecklistItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    item_code: str
    item_name: str
    checklist_version: int
    # 已提交结果（无则为空，表示该检查项尚未完成）
    result_status: str | None = None
    measured_value: str = ""
    photo_url: str = ""
    note: str = ""
    submitted_by: int | None = None
    submitted_by_name: str = ""
    submitted_at: datetime | None = None
    hazard_id: int | None = None
    hazard_status: str | None = None


class InspectionTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    building_id: int
    building_name: str = ""
    inspector_id: int | None = None
    inspector_name: str = ""
    plan_date: datetime | None = None
    task_type: str
    status: str
    checklist_version: int
    finished_at: datetime | None = None
    reviewed_at: datetime | None = None
    created_at: datetime | None = None
    total_items: int = 0
    submitted_items: int = 0
    abnormal_items: int = 0
    open_hazard_count: int = 0
    items: list[ChecklistItemDTO] = []
