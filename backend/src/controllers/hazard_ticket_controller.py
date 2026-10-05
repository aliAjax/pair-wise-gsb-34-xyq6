from fastapi import Depends, Query
from sqlalchemy.orm import Session

from src.database.session import get_session
from src.middlewares.rbac_middleware import (
    current_user,
    require_maintainer,
    require_supervisor,
)
from src.services.hazard_ticket_service import HazardTicketService
from src.types.hazard_ticket_payload import (
    AssignHazardPayload,
    CloseHazardPayload,
    RectifyHazardPayload,
)


def list_hazard_ticket(
    rectify_status: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    owner_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
    actor: dict = Depends(current_user),
):
    return HazardTicketService(session).list(
        rectify_status=rectify_status, severity=severity, owner_id=owner_id
    )


def assign_hazard_ticket(
    ticket_id: int,
    payload: AssignHazardPayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_supervisor),
):
    return HazardTicketService(session).assign(ticket_id, payload, actor)


def rectify_hazard_ticket(
    ticket_id: int,
    payload: RectifyHazardPayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_maintainer),
):
    return HazardTicketService(session).rectify(ticket_id, payload, actor)


def close_hazard_ticket(
    ticket_id: int,
    payload: CloseHazardPayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_supervisor),
):
    return HazardTicketService(session).close(ticket_id, payload, actor)
