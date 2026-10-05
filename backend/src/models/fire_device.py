from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FireDevice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    building_id: int
    building_name: str = ""
    device_code: str
    device_type: str
    floor: str
    location_desc: str
    install_date: datetime | None = None
    status: str
    next_maintenance_at: datetime | None = None
    open_hazard_count: int = 0
