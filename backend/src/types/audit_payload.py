from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    actor: str
    action: str
    target_type: str
    target_id: str
    detail: str | None
    created_at: str | None
