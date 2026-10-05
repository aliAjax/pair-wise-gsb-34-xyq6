from pydantic import BaseModel, ConfigDict


class Building(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    campus: str
    floor_count: int
    fire_grade: str
    manager_id: int | None = None
    address_code: str = ""
    manager_name: str = ""
    device_count: int = 0
    task_count: int = 0
