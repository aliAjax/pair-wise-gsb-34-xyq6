from pydantic import BaseModel, field_validator


class ResultItemPayload(BaseModel):
    device_id: int
    item_code: str
    result_status: str
    measured_value: str | None = None
    photo_url: str | None = None
    note: str | None = None

    @field_validator("result_status")
    @classmethod
    def validate_result(cls, value):
        from src.constants.result_status import ResultStatus

        if value not in ResultStatus:
            raise ValueError("result_status 只能是 NORMAL 或 ABNORMAL")
        return value


class ResultSubmitPayload(BaseModel):
    # 巡检员拉清单时看到的版本；服务端据此判断清单是否过期。
    checklist_version: str
    items: list[ResultItemPayload]

    @field_validator("items")
    @classmethod
    def non_empty(cls, value):
        if not value:
            raise ValueError("至少提交一个检查项")
        return value


class RejectedItem(BaseModel):
    device_id: int | None = None
    item_code: str
    reason_code: str
    reason: str


class InspectionResultResponse(BaseModel):
    id: int
    task_id: int
    device_id: int
    item_code: str
    result_status: str
    measured_value: str | None
    photo_url: str | None
    note: str | None
    checklist_version: str
