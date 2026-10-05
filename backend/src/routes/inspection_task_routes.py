from fastapi import APIRouter

from src.controllers.inspection_task_controller import (
    bump_checklist_version,
    claim_inspection_task,
    create_inspection_task,
    get_inspection_task,
    list_inspection_task,
    review_inspection_task,
    submit_inspection_task,
)

router = APIRouter(prefix="/api/inspection-task", tags=["InspectionTask"])
router.get("", response_model=None)(list_inspection_task)
router.get("/{task_id}", response_model=None)(get_inspection_task)
router.post("", response_model=None)(create_inspection_task)
router.post("/{task_id}/claim", response_model=None)(claim_inspection_task)
router.post("/{task_id}/submit", response_model=None)(submit_inspection_task)
router.post("/{task_id}/review", response_model=None)(review_inspection_task)
router.post("/{task_id}/checklist-version", response_model=None)(bump_checklist_version)
