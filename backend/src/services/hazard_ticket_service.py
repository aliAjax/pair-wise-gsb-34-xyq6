from datetime import date, datetime

from sqlalchemy.orm import Session

from src.constants.device_status import MAINTAINING
from src.constants.hazard_severity import HazardSeverity
from src.constants.rectify_status import (
    ASSIGNED,
    CLOSED,
    MAINTAINABLE_STATUSES,
    OPEN,
    RECTIFIED,
    REJECTED,
    REVIEWABLE_STATUSES,
)
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.user_repository import UserRepository
from src.services.audit_service import write_audit_log
from src.services.device_status_service import DeviceStatusRecalculator
from src.services.errors import ConflictError, NotFoundError, ServiceError


class HazardTicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = HazardTicketRepository(db)
        self.device_repo = FireDeviceRepository(db)
        self.user_repo = UserRepository(db)
        self.recalculator = DeviceStatusRecalculator(db)

    def list(self, rectify_status: str | None = None, device_id: int | None = None):
        return self.repo.find_all(rectify_status=rectify_status, device_id=device_id)

    def get(self, ticket_id: int):
        ticket = self.repo.get(ticket_id)
        if not ticket:
            raise NotFoundError("隐患单不存在")
        return ticket

    def assign(self, ticket_id: int, payload, actor: dict):
        """主管派单：指定维保责任人、级别和期限。"""
        ticket = self.get(ticket_id)
        if ticket.rectify_status not in (OPEN, REJECTED):
            raise ConflictError("TICKET_NOT_ACTIONABLE", "仅待派单或复验退回的隐患单可以派单")
        owner = self.user_repo.get(payload.owner_id)
        if not owner:
            raise ServiceError("NOT_FOUND", "指定的维保人员不存在")
        from src.constants.roles import ROLE_MAINTAINER

        if owner.role != ROLE_MAINTAINER:
            raise ServiceError("VALIDATION_FAILED", "责任人必须是维保人员")
        if payload.severity and payload.severity not in HazardSeverity:
            raise ServiceError("VALIDATION_FAILED", "未知的隐患级别")

        ticket.owner_id = payload.owner_id
        if payload.severity:
            ticket.severity = payload.severity
        if payload.deadline:
            ticket.deadline = date.fromisoformat(payload.deadline)
        ticket.rectify_status = ASSIGNED
        self.db.flush()

        device = self.device_repo.get(ticket.device_id)
        if device:
            device.status = MAINTAINING
            self.db.flush()

        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="HazardTicket",
            event="HazardTicket.assign",
            target_type="HazardTicket",
            target_id=ticket.id,
            ticket_id=ticket.id,
            owner_id=payload.owner_id,
        )
        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="FireDevice",
            event="FireDevice.status",
            target_type="FireDevice",
            target_id=device.id if device else ticket.device_id,
            device_id=ticket.device_id,
            status=MAINTAINING,
        )
        self.db.commit()
        return ticket

    def rectify(self, ticket_id: int, payload, actor: dict):
        """维保人员提交整改说明，隐患单进入待复验。"""
        ticket = self.get(ticket_id)
        if ticket.rectify_status not in MAINTAINABLE_STATUSES:
            raise ConflictError("TICKET_NOT_ACTIONABLE", "隐患单当前状态不允许提交整改")
        if ticket.owner_id != actor["id"]:
            from src.services.errors import RbacError

            raise RbacError("只有被派单的维保人员才能提交整改说明")

        ticket.rectify_status = RECTIFIED
        ticket.rectify_note = payload.rectify_note
        self.db.flush()
        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="HazardTicket",
            event="HazardTicket.rectify",
            target_type="HazardTicket",
            target_id=ticket.id,
            ticket_id=ticket.id,
            owner_id=actor["id"],
        )
        # 整改提交后重新计算设备状态（仍有其他整改中单则保持整改中，否则故障待验）。
        self.recalculator.recalculate(ticket.device_id)
        self.db.commit()
        return ticket

    def review(self, ticket_id: int, approved: bool, note: str | None, actor: dict):
        """主管复验：通过即关闭并恢复设备；不通过退回维保重新整改。"""
        ticket = self.get(ticket_id)
        if ticket.rectify_status not in REVIEWABLE_STATUSES:
            raise ConflictError("TICKET_NOT_ACTIONABLE", "仅待复验的隐患单可以执行复验")

        if approved:
            ticket.rectify_status = CLOSED
            ticket.closed_at = datetime.now()
            if note:
                ticket.rectify_note = (ticket.rectify_note or "") + f"\n[复验意见] {note}"
            event = "HazardTicket.close"
        else:
            ticket.rectify_status = REJECTED
            if note:
                ticket.rectify_note = (ticket.rectify_note or "") + f"\n[复验退回] {note}"
            event = "HazardTicket.reject"
        self.db.flush()

        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="HazardTicket",
            event=event,
            target_type="HazardTicket",
            target_id=ticket.id,
            ticket_id=ticket.id,
            device_id=ticket.device_id,
        )
        # 复验闭环后按剩余未闭环隐患重算设备状态（无隐患则恢复正常）。
        device = self.recalculator.recalculate(ticket.device_id)
        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="FireDevice",
            event="FireDevice.status",
            target_type="FireDevice",
            target_id=ticket.device_id,
            device_id=ticket.device_id,
            status=device.status if device else "UNKNOWN",
        )
        self.db.commit()
        return ticket

    def counts(self):
        return self.repo.count_by_status()
