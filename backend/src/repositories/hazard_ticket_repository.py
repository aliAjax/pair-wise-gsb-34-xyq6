from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.entities import HazardTicket


class HazardTicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(
        self,
        rectify_status: str | None = None,
        severity: str | None = None,
        owner_id: int | None = None,
    ) -> list[HazardTicket]:
        stmt = (
            select(HazardTicket)
            .options(selectinload(HazardTicket.result))
            .order_by(HazardTicket.id.desc())
        )
        if rectify_status is not None:
            stmt = stmt.where(HazardTicket.rectify_status == rectify_status)
        if severity is not None:
            stmt = stmt.where(HazardTicket.severity == severity)
        if owner_id is not None:
            stmt = stmt.where(HazardTicket.owner_id == owner_id)
        return list(self.session.scalars(stmt))

    def get(self, ticket_id: int) -> HazardTicket | None:
        stmt = (
            select(HazardTicket)
            .where(HazardTicket.id == ticket_id)
            .options(selectinload(HazardTicket.result))
        )
        return self.session.scalars(stmt).first()

    def add(self, ticket: HazardTicket) -> HazardTicket:
        self.session.add(ticket)
        self.session.flush()
        return ticket
