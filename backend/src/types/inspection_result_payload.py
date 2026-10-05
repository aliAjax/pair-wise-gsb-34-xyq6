from typing import Literal

from pydantic import BaseModel, Field


class ResultItemPayload(BaseModel):
    item_code: str = Field(min_length=1, max_length=64)
    # 巡检员打开清单时看到的版本；服务端据此识别过期清单
    checklist_version: int = Field(ge=1)
    result_status: Literal["NORMAL", "ABNORMAL"]
    measured_value: str = Field(default="", max_length=255)
    photo_url: str = Field(default="", max_length=255)
    note: str = Field(default="", max_length=1000)
    severity: str | None = None


class ResultBatchPayload(BaseModel):
    items: list[ResultItemPayload] = Field(min_length=1)
