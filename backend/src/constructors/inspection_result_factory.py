"""巡检结果 ORM 实体 -> 响应 DTO 的构造器。"""

from src.models.entities import InspectionResult


def create_inspection_result_dto(result: InspectionResult | None = None, **overrides) -> dict:
    if result is None:
        row = {
            "id": 0,
            "task_id": 0,
            "device_id": 0,
            "item_code": "",
            "result_status": "NORMAL",
            "measured_value": "",
            "photo_url": "",
            "note": "",
        }
    else:
        row = {
            "id": result.id,
            "task_id": result.task_id,
            "device_id": result.device_id,
            "item_name": overrides.pop("item_name", ""),
            "item_code": result.item_code,
            "result_status": result.result_status,
            "measured_value": result.measured_value,
            "photo_url": result.photo_url,
            "note": result.note,
            "submitted_by": result.submitted_by,
            "submitted_by_name": overrides.pop("submitter_name", ""),
            "submitted_at": result.submitted_at,
            "device_code": overrides.pop("device_code", ""),
            "building_name": overrides.pop("building_name", ""),
            "hazard_id": result.hazard.id if result.hazard else None,
        }
    row.update(overrides)
    return row


def create_inspection_result_form(**overrides) -> dict:
    return create_inspection_result_dto(None, **overrides)


def create_inspection_result_response(result: InspectionResult, **overrides) -> dict:
    return create_inspection_result_dto(result, **overrides)
