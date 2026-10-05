from fastapi import Depends, Query
from sqlalchemy.orm import Session

from src.database.session import get_session
from src.middlewares.rbac_middleware import current_user, require_inspector, require_supervisor
from src.services.inspection_task_service import InspectionTaskService
from src.types.inspection_task_payload import InspectionTaskPayload, ReviewPayload


def list_inspection_task(
    building_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    session: Session = Depends(get_session),
    actor: dict = Depends(current_user),
):
    return InspectionTaskService(session).list(building_id=building_id, status=status)


def get_inspection_task(
    task_id: int,
    session: Session = Depends(get_session),
    actor: dict = Depends(current_user),
):
    return InspectionTaskService(session).detail(task_id)


def create_inspection_task(
    payload: InspectionTaskPayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_supervisor),
):
    return InspectionTaskService(session).create(payload, actor)


def claim_inspection_task(
    task_id: int,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_inspector),
):
    return InspectionTaskService(session).claim(task_id, actor)


def submit_inspection_task(
    task_id: int,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_inspector),
):
    return InspectionTaskService(session).submit_for_review(task_id, actor)


def review_inspection_task(
    task_id: int,
    payload: ReviewPayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_supervisor),
):
    return InspectionTaskService(session).review(task_id, payload.note, actor)


def bump_checklist_version(
    task_id: int,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_supervisor),
):
    return InspectionTaskService(session).bump_checklist_version(task_id, actor)
