from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.constants.roles import ROLE_INSPECTOR, ROLE_SUPERVISOR
from src.constructors.inspection_task_factory import build_inspection_task_list, build_inspection_task_response
from src.db.session import get_db
from src.middlewares.rbac_middleware import current_user, require_roles
from src.services.inspection_task_service import InspectionTaskService
from src.types.inspection_task_payload import ChecklistPublishPayload, InspectionTaskCreatePayload

router = APIRouter()


@router.get("")
def list_inspection_task(
    building_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    service = InspectionTaskService(db)
    return build_inspection_task_list(service.list(building_id=building_id, status=status))


@router.post("")
def create_inspection_task(
    payload: InspectionTaskCreatePayload,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_SUPERVISOR)),
):
    service = InspectionTaskService(db)
    task = service.create_task(payload, user)
    return build_inspection_task_response(task)


# 静态路径必须在 /{task_id}/... 之前注册，避免被路径参数吞掉。
@router.post("/checklist/publish")
def publish_checklist(
    payload: ChecklistPublishPayload,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_SUPERVISOR)),
):
    service = InspectionTaskService(db)
    return service.publish_checklist(payload, user)


@router.post("/{task_id}/claim")
def claim_inspection_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_INSPECTOR)),
):
    service = InspectionTaskService(db)
    task = service.claim(task_id, user)
    return build_inspection_task_response(task)


@router.get("/{task_id}/checklist")
def get_task_checklist(
    task_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    # 清单只读：登录后的各角色均可查看，写动作仍在各自接口上做角色拦截。
    service = InspectionTaskService(db)
    return service.checklist(task_id)


@router.post("/{task_id}/review")
def review_inspection_task(
    task_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_SUPERVISOR)),
):
    service = InspectionTaskService(db)
    approved = bool(payload.get("approved", True))
    task = service.review(task_id, approved, user)
    return build_inspection_task_response(task)
