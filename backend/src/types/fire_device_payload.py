from datetime import date

from pydantic import BaseModel, Field


class FireDevicePayload(BaseModel):
    building_id: int
    device_code: str = Field(min_length=1, max_length=64)
    device_type: str
    floor: str = Field(default="1", max_length=16)
    location_desc: str = Field(default="", max_length=255)
    install_date: date | None = None
    next_maintenance_at: date | None = None
