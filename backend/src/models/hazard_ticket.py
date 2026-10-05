from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HazardTicket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    result_id: int
    task_id: int = 0
    device_id: int = 0
    device_code: str = ""
    building_name: str = ""
    item_code: str = ""
    item_name: str = ""
    result_note: str = ""
    severity: str
    owner_id: int | None = None
    owner_name: str = ""
    deadline: datetime | None = None
    rectify_status: str
    rectify_note: str = ""
    created_at: datetime | None = None
    rectified_at: datetime | None = None
    closed_at: datetime | None = None
    closed_by: int | None = None
    overdue: bool = False
