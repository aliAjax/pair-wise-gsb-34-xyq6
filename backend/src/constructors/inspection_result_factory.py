from src.models.inspection_result import InspectionResult
from src.types.inspection_result_payload import InspectionResultResponse


def build_inspection_result_response(result: InspectionResult) -> InspectionResultResponse:
    return InspectionResultResponse(
        id=result.id,
        task_id=result.task_id,
        device_id=result.device_id,
        item_code=result.item_code,
        result_status=result.result_status,
        measured_value=result.measured_value,
        photo_url=result.photo_url,
        note=result.note,
        checklist_version=result.checklist_version,
    )


def build_inspection_result_list(results) -> list[InspectionResultResponse]:
    return [build_inspection_result_response(row) for row in results]
