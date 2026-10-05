from fastapi import APIRouter

from src.controllers.hazard_ticket_controller import (
    assign_hazard_ticket,
    close_hazard_ticket,
    list_hazard_ticket,
    rectify_hazard_ticket,
)

router = APIRouter(prefix="/api/hazard-ticket", tags=["HazardTicket"])
router.get("", response_model=None)(list_hazard_ticket)
router.post("/{ticket_id}/assign", response_model=None)(assign_hazard_ticket)
router.post("/{ticket_id}/rectify", response_model=None)(rectify_hazard_ticket)
router.post("/{ticket_id}/close", response_model=None)(close_hazard_ticket)
