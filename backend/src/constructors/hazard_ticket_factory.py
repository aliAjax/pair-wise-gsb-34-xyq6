from src.models.hazard_ticket import HazardTicket
from src.types.hazard_ticket_payload import HazardTicketResponse


def build_hazard_ticket_response(ticket: HazardTicket) -> HazardTicketResponse:
    return HazardTicketResponse(
        id=ticket.id,
        result_id=ticket.result_id,
        device_id=ticket.device_id,
        severity=ticket.severity,
        owner_id=ticket.owner_id,
        deadline=ticket.deadline.isoformat() if ticket.deadline else None,
        rectify_status=ticket.rectify_status,
        rectify_note=ticket.rectify_note,
        closed_at=ticket.closed_at.isoformat() if ticket.closed_at else None,
    )


def build_hazard_ticket_list(tickets) -> list[HazardTicketResponse]:
    return [build_hazard_ticket_response(row) for row in tickets]
