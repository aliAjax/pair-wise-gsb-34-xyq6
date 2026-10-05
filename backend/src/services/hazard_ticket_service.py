"""隐患整改单：派单 -> 维保整改 -> 主管复验关闭，关闭后设备状态重算。"""

from datetime import timedelta

from sqlalchemy.orm import Session

from src.constants.hazard_severity import HazardSeverity
from src.constructors.hazard_ticket_factory import create_hazard_ticket_response
from src.constants.user_role import ROLE_MAINTAINER, ROLE_SUPERVISOR
from src.middlewares.rbac_middleware import assert_role
from src.models.entities import HazardTicket, utcnow
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.user_repository import UserRepository
from src.services.audit_service import write_audit
from src.services.fire_device_service import FireDeviceService
from src.services.errors import BusinessError, ConflictError, NotFoundError
from src.types.hazard_ticket_payload import (
    AssignHazardPayload,
    CloseHazardPayload,
    RectifyHazardPayload,
)

_DEFAULT_DEADLINE_DAYS = 7


class HazardTicketService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = HazardTicketRepository(session)
        self.user_repo = UserRepository(session)
        self.task_repo = InspectionTaskRepository(session)
        self.device_repo = FireDeviceRepository(session)

    def list(
        self,
        rectify_status: str | None = None,
        severity: str | None = None,
        owner_id: int | None = None,
    ) -> list[dict]:
        tickets = self.repo.find_all(
            rectify_status=rectify_status, severity=severity, owner_id=owner_id
        )
        return [self._to_dto(t) for t in tickets]

    def _to_dto(self, ticket: HazardTicket) -> dict:
        result = ticket.result
        task = self.task_repo.get(result.task_id) if result is not None else None
        device = self.device_repo.get(result.device_id) if result is not None else None
        item_name = ""
        building_name = ""
        if task is not None:
            building_name = task.building.name if task.building else ""
            item = next((i for i in task.items if i.item_code == result.item_code), None)
            item_name = item.item_name if item else ""
        owner = self.user_repo.get(ticket.owner_id) if ticket.owner_id else None
        return create_hazard_ticket_response(
            ticket,
            device_code=device.device_code if device else "",
            building_name=building_name,
            item_name=item_name,
            owner_name=owner.name if owner else "",
        )

    def _get(self, ticket_id: int) -> HazardTicket:
        ticket = self.repo.get(ticket_id)
        if ticket is None:
            raise NotFoundError("HAZARD_NOT_FOUND")
        return ticket

    def assign(self, ticket_id: int, payload: AssignHazardPayload, actor: dict) -> dict:
        """主管分级派单给维保人员。"""
        assert_role(actor, ROLE_SUPERVISOR)
        ticket = self._get(ticket_id)
        if ticket.rectify_status not in ("OPEN",):
            raise ConflictError("HAZARD_NOT_ASSIGNABLE")
        owner = self.user_repo.get(payload.owner_id)
        if owner is None or owner.role != ROLE_MAINTAINER:
            raise BusinessError(
                "VALIDATION_FAILED", "责任人必须是维保人员", status_code=422
            )
        if payload.severity is not None:
            if payload.severity not in HazardSeverity:
                raise BusinessError("VALIDATION_FAILED", "隐患级别不合法", status_code=422)
            ticket.severity = payload.severity
        ticket.owner_id = owner.id
        ticket.deadline = payload.deadline or (utcnow() + timedelta(days=_DEFAULT_DEADLINE_DAYS))
        ticket.rectify_status = "ASSIGNED"
        write_audit(
            self.session, actor, "HazardTicket.assign", "HazardTicket", ticket.id,
            f"隐患派单给 {owner.name}，级别 {ticket.severity}，期限 {ticket.deadline:%Y-%m-%d}",
        )
        self.session.commit()
        return self._to_dto(ticket)

    def rectify(self, ticket_id: int, payload: RectifyHazardPayload, actor: dict) -> dict:
        """维保人员提交整改结果。"""
        assert_role(actor, ROLE_MAINTAINER)
        ticket = self._get(ticket_id)
        if ticket.rectify_status != "ASSIGNED" or ticket.owner_id != actor["id"]:
            raise ConflictError("HAZARD_NOT_RECTIFIABLE")
        ticket.rectify_status = "RECTIFIED"
        ticket.rectify_note = payload.rectify_note
        ticket.rectified_at = utcnow()
        write_audit(
            self.session, actor, "HazardTicket.rectify", "HazardTicket", ticket.id,
            f"维保整改完成：{payload.rectify_note}",
        )
        self.session.commit()
        return self._to_dto(ticket)

    def close(self, ticket_id: int, payload: CloseHazardPayload, actor: dict) -> dict:
        """主管复验：通过则关闭并重算设备状态；不通过退回整改。"""
        assert_role(actor, ROLE_SUPERVISOR)
        ticket = self._get(ticket_id)
        if ticket.rectify_status != "RECTIFIED":
            raise ConflictError("HAZARD_NOT_CLOSABLE")

        if not payload.pass_review:
            ticket.rectify_status = "ASSIGNED"
            ticket.rectified_at = None
            ticket.rectify_note = f"{ticket.rectify_note} / 复验不通过退回：{payload.note}".strip(" /")
            write_audit(
                self.session, actor, "HazardTicket.update", "HazardTicket", ticket.id,
                f"复验不通过退回维保：{payload.note}",
            )
            self.session.commit()
            FireDeviceService(self.session).recalculate_status(ticket.result.device_id, actor)
            self.session.commit()
            return self._to_dto(ticket)

        ticket.rectify_status = "CLOSED"
        ticket.closed_at = utcnow()
        ticket.closed_by = actor["id"]
        if payload.note:
            ticket.rectify_note = f"{ticket.rectify_note} / 复验结论：{payload.note}".strip(" /")
        write_audit(
            self.session, actor, "HazardTicket.close", "HazardTicket", ticket.id,
            f"复验通过关闭隐患单：{payload.note or '合格'}",
        )
        self.session.commit()
        # 关闭后消防设备状态与总览重新计算
        FireDeviceService(self.session).recalculate_status(ticket.result.device_id, actor)
        self.session.commit()
        return self._to_dto(ticket)
