"""隐患整改单 ORM 实体 -> 响应 DTO 的构造器。

跨实体冗余字段（楼栋名、设备编号、检查项名称、责任人姓名）由 service
查询后通过 overrides 注入，保持构造器只做字段拼装。
"""

from src.models.entities import HazardTicket
from src.models.entities import utcnow


def create_hazard_ticket_dto(ticket: HazardTicket | None = None, **overrides) -> dict:
    if ticket is None:
        row = {
            "id": 0,
            "result_id": 0,
            "severity": "MEDIUM",
            "rectify_status": "OPEN",
            "rectify_note": "",
        }
    else:
        result = ticket.result
        overdue = bool(
            ticket.rectify_status != "CLOSED"
            and ticket.deadline is not None
            and ticket.deadline < utcnow()
        )
        row = {
            "id": ticket.id,
            "result_id": ticket.result_id,
            "task_id": result.task_id if result else 0,
            "device_id": result.device_id if result else 0,
            "device_code": overrides.pop("device_code", ""),
            "building_name": overrides.pop("building_name", ""),
            "item_code": result.item_code if result else "",
            "item_name": overrides.pop("item_name", ""),
            "result_note": result.note if result else "",
            "severity": ticket.severity,
            "owner_id": ticket.owner_id,
            "owner_name": overrides.pop("owner_name", ""),
            "deadline": ticket.deadline,
            "rectify_status": ticket.rectify_status,
            "rectify_note": ticket.rectify_note,
            "created_at": ticket.created_at,
            "rectified_at": ticket.rectified_at,
            "closed_at": ticket.closed_at,
            "closed_by": ticket.closed_by,
            "overdue": overdue,
        }
    row.update(overrides)
    return row


def create_hazard_ticket_form(**overrides) -> dict:
    return create_hazard_ticket_dto(None, **overrides)


def create_hazard_ticket_response(ticket: HazardTicket, **overrides) -> dict:
    return create_hazard_ticket_dto(ticket, **overrides)
