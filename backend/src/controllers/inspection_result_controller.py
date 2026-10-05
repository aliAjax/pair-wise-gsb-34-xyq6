from fastapi import Depends, Query
from sqlalchemy.orm import Session

from src.database.session import get_session
from src.middlewares.rbac_middleware import current_user, require_inspector
from src.services.inspection_result_service import InspectionResultService
from src.types.inspection_result_payload import ResultBatchPayload


def list_inspection_result(
    task_id: int | None = Query(default=None),
    device_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
    actor: dict = Depends(current_user),
):
    return InspectionResultService(session).list(task_id=task_id, device_id=device_id)


def submit_inspection_results(
    task_id: int,
    payload: ResultBatchPayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_inspector),
):
    return InspectionResultService(session).batch_submit(task_id, payload, actor)
