from pydantic import BaseModel, ConfigDict


class HazardTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    result_id: int
    device_id: int
    severity: str
    owner_id: int | None
    deadline: str | None
    rectify_status: str
    rectify_note: str | None
    closed_at: str | None


class HazardAssignPayload(BaseModel):
    owner_id: int
    severity: str | None = None
    deadline: str | None = None


class HazardRectifyPayload(BaseModel):
    rectify_note: str


class HazardReviewPayload(BaseModel):
    approved: bool
    rectify_note: str | None = None
