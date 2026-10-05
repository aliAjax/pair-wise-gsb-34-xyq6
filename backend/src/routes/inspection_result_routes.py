from fastapi import APIRouter

from src.controllers.inspection_result_controller import (
    list_inspection_result,
    submit_inspection_results,
)

router = APIRouter(prefix="/api/inspection-result", tags=["InspectionResult"])
router.get("", response_model=None)(list_inspection_result)
router.post("/task/{task_id}/submit", response_model=None)(submit_inspection_results)
