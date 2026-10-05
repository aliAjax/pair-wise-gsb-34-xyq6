from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.constants.roles import ROLE_INSPECTOR
from src.constructors.inspection_result_factory import build_inspection_result_list
from src.db.session import get_db
from src.middlewares.rbac_middleware import current_user, require_roles
from src.services.inspection_result_service import InspectionResultService
from src.types.inspection_result_payload import ResultSubmitPayload

router = APIRouter()


@router.get("")
def list_inspection_result(
    task_id: int | None = Query(default=None),
    device_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    service = InspectionResultService(db)
    return build_inspection_result_list(service.list(task_id=task_id, device_id=device_id))


@router.post("/task/{task_id}/submit")
def submit_inspection_result(
    task_id: int,
    payload: ResultSubmitPayload,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_INSPECTOR)),
):
    # Controller 层只做入参解析与角色拦截；版本冲突/并发互斥由 Service 层判定。
    service = InspectionResultService(db)
    return service.submit(task_id, payload, user)
