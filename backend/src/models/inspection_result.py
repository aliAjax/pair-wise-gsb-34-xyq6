from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InspectionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    device_id: int
    item_code: str
    item_name: str = ""
    result_status: str
    measured_value: str = ""
    photo_url: str = ""
    note: str = ""
    submitted_by: int | None = None
    submitted_by_name: str = ""
    submitted_at: datetime | None = None
    device_code: str = ""
    building_name: str = ""
    hazard_id: int | None = None
