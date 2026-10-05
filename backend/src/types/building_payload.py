from pydantic import BaseModel, ConfigDict


class BuildingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    campus: str
    floor_count: int
    fire_grade: str
    manager_id: int | None
    address_code: str | None
