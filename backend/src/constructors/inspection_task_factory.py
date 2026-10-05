from src.models.inspection_result import InspectionResult
from src.models.inspection_task import ChecklistItem, InspectionTask
from src.types.inspection_task_payload import ChecklistItemResponse, InspectionTaskResponse


def build_inspection_task_response(task: InspectionTask) -> InspectionTaskResponse:
    return InspectionTaskResponse(
        id=task.id,
        building_id=task.building_id,
        inspector_id=task.inspector_id,
        plan_date=task.plan_date,
        task_type=task.task_type,
        status=task.status,
        checklist_version=task.checklist_version,
        finished_at=task.finished_at.isoformat() if task.finished_at else None,
    )


def build_inspection_task_list(tasks) -> list[InspectionTaskResponse]:
    return [build_inspection_task_response(row) for row in tasks]


def build_checklist_item_response(item: ChecklistItem, result: InspectionResult | None = None) -> ChecklistItemResponse:
    return ChecklistItemResponse(
        item_code=item.item_code,
        item_name=item.item_name,
        checklist_version=item.checklist_version,
        deprecated=item.deprecated,
        filled=result is not None,
        result_status=result.result_status if result else None,
    )
