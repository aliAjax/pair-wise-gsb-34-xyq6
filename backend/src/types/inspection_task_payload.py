from pydantic import BaseModel, ConfigDict


class ChecklistItemPayload(BaseModel):
    item_code: str
    item_name: str


class InspectionTaskCreatePayload(BaseModel):
    building_id: int
    plan_date: str
    task_type: str


class InspectionTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    building_id: int
    inspector_id: int | None
    plan_date: str
    task_type: str
    status: str
    checklist_version: str
    finished_at: str | None


class ChecklistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_code: str
    item_name: str
    checklist_version: str
    deprecated: bool
    filled: bool = False
    result_status: str | None = None


class ChecklistPublishPayload(BaseModel):
    task_type: str
    items: list[ChecklistItemPayload]
