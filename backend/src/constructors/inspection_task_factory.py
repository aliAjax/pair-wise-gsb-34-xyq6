"""巡检任务/清单 ORM 实体 -> 响应 DTO 的构造器。"""

from src.models.entities import InspectionResult, InspectionTask, TaskChecklistItem


def create_checklist_item_dto(
    item: TaskChecklistItem,
    result: InspectionResult | None = None,
    **overrides,
) -> dict:
    row = {
        "id": item.id,
        "device_id": item.device_id,
        "item_code": item.item_code,
        "item_name": item.item_name,
        "checklist_version": item.checklist_version,
        "result_status": result.result_status if result else None,
        "measured_value": result.measured_value if result else "",
        "photo_url": result.photo_url if result else "",
        "note": result.note if result else "",
        "submitted_by": result.submitted_by if result else None,
        "submitted_by_name": "",  # 由 service 注入提交人姓名
        "submitted_at": result.submitted_at if result else None,
        "hazard_id": result.hazard.id if result and result.hazard else None,
        "hazard_status": result.hazard.rectify_status if result and result.hazard else None,
    }
    if result is not None:
        row["submitted_by_name"] = overrides.pop("submitter_name", "")
    row.update(overrides)
    return row


def create_inspection_task_dto(task: InspectionTask | None = None, **overrides) -> dict:
    if task is None:
        row = {
            "id": 0,
            "building_id": 0,
            "task_type": "HYDRANT",
            "plan_date": None,
            "inspector_id": None,
            "status": "PLANNED",
            "checklist_version": 1,
        }
    else:
        result_by_code = {r.item_code: r for r in task.results}
        row = {
            "id": task.id,
            "building_id": task.building_id,
            "building_name": task.building.name if task.building else "",
            "inspector_id": task.inspector_id,
            "inspector_name": task.inspector.name if task.inspector else "",
            "plan_date": task.plan_date,
            "task_type": task.task_type,
            "status": task.status,
            "checklist_version": task.checklist_version,
            "finished_at": task.finished_at,
            "reviewed_at": task.reviewed_at,
            "created_at": task.created_at,
            "total_items": len(task.items),
            "submitted_items": len(task.results),
            "abnormal_items": sum(1 for r in task.results if r.result_status == "ABNORMAL"),
            "open_hazard_count": sum(
                1 for r in task.results if r.hazard and r.hazard.rectify_status != "CLOSED"
            ),
            "items": [
                create_checklist_item_dto(item, result_by_code.get(item.item_code))
                for item in sorted(task.items, key=lambda i: (i.device_id, i.id))
            ],
        }
    row.update(overrides)
    return row


def create_inspection_task_form(**overrides) -> dict:
    return create_inspection_task_dto(None, **overrides)


def create_inspection_task_response(task: InspectionTask, **overrides) -> dict:
    return create_inspection_task_dto(task, **overrides)
