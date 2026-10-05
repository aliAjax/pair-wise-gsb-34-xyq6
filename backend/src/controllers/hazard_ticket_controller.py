from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.constants.roles import ROLE_MAINTAINER, ROLE_SUPERVISOR
from src.constructors.hazard_ticket_factory import build_hazard_ticket_list, build_hazard_ticket_response
from src.db.session import get_db
from src.middlewares.rbac_middleware import current_user, require_roles
from src.services.hazard_ticket_service import HazardTicketService
from src.types.hazard_ticket_payload import HazardAssignPayload, HazardRectifyPayload, HazardReviewPayload

router = APIRouter()


@router.get("")
def list_hazard_ticket(
    rectify_status: str | None = Query(default=None),
    device_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    service = HazardTicketService(db)
    return build_hazard_ticket_list(service.list(rectify_status=rectify_status, device_id=device_id))


@router.post("/{ticket_id}/assign")
def assign_hazard_ticket(
    ticket_id: int,
    payload: HazardAssignPayload,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_SUPERVISOR)),
):
    service = HazardTicketService(db)
    ticket = service.assign(ticket_id, payload, user)
    return build_hazard_ticket_response(ticket)


@router.post("/{ticket_id}/rectify")
def rectify_hazard_ticket(
    ticket_id: int,
    payload: HazardRectifyPayload,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_MAINTAINER)),
):
    service = HazardTicketService(db)
    ticket = service.rectify(ticket_id, payload, user)
    return build_hazard_ticket_response(ticket)


@router.post("/{ticket_id}/review")
def review_hazard_ticket(
    ticket_id: int,
    payload: HazardReviewPayload,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_SUPERVISOR)),
):
    service = HazardTicketService(db)
    ticket = service.review(ticket_id, payload.approved, payload.rectify_note, user)
    return build_hazard_ticket_response(ticket)
