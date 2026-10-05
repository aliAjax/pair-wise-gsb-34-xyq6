from pydantic import BaseModel, ConfigDict


class FireDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    building_id: int
    device_code: str
    device_type: str
    floor: str
    location_desc: str
    install_date: str | None
    status: str
    next_maintenance_at: str | None


class FireDeviceCreatePayload(BaseModel):
    building_id: int
    device_code: str
    device_type: str
    floor: str
    location_desc: str
    install_date: str | None = None
    next_maintenance_at: str | None = None


class FireDeviceStatusPayload(BaseModel):
    status: str
