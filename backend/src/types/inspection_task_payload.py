from datetime import datetime

from pydantic import BaseModel, Field


class InspectionTaskPayload(BaseModel):
    """主管按楼栋排期：同楼栋同设备类型会生成标准检查清单。"""

    building_id: int
    task_type: str
    plan_date: datetime | None = None


class ReviewPayload(BaseModel):
    note: str = Field(default="", max_length=1000)
