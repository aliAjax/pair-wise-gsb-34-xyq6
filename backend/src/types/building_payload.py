from datetime import date

from pydantic import BaseModel, Field


class BuildingPayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    campus: str = Field(min_length=1, max_length=128)
    floor_count: int = Field(ge=1, le=200)
    fire_grade: str = Field(default="二级", max_length=32)
    manager_id: int | None = None
    address_code: str = Field(default="", max_length=64)
