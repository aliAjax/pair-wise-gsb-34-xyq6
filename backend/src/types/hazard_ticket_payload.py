from datetime import datetime

from pydantic import BaseModel, Field


class AssignHazardPayload(BaseModel):
    owner_id: int
    deadline: datetime | None = None
    severity: str | None = None


class RectifyHazardPayload(BaseModel):
    rectify_note: str = Field(min_length=1, max_length=1000)


class CloseHazardPayload(BaseModel):
    note: str = Field(default="", max_length=1000)
    pass_review: bool = True
