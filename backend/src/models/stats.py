from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    actor_name: str
    actor_role: str
    action: str
    action_label: str
    target_type: str
    target_id: str
    detail: str
    created_at: datetime | None = None


class DashboardStats(BaseModel):
    device_total: int
    device_normal: int
    device_fault: int
    device_maintaining: int
    device_scrapped: int
    open_hazard_total: int
    overdue_hazard_total: int
    critical_hazard_total: int
    task_total: int
    task_finished: int
    inspection_completion_rate: float
    rectification_rate: float


class MonthlyReportRow(BaseModel):
    month: str
    task_total: int
    task_finished: int
    inspection_rate: float
    hazard_total: int
    hazard_closed: int
    rectification_rate: float
    abnormal_device_count: int
