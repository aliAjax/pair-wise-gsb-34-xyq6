from sqlalchemy.orm import Session

from src.models.hazard_ticket import AuditLog, HazardTicket


class HazardTicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self, rectify_status: str | None = None, device_id: int | None = None):
        query = self.db.query(HazardTicket)
        if rectify_status is not None:
            query = query.filter(HazardTicket.rectify_status == rectify_status)
        if device_id is not None:
            query = query.filter(HazardTicket.device_id == device_id)
        return query.order_by(HazardTicket.id.desc()).all()

    def get(self, ticket_id: int) -> HazardTicket | None:
        return self.db.get(HazardTicket, ticket_id)

    def get_by_result(self, result_id: int) -> HazardTicket | None:
        return (
            self.db.query(HazardTicket)
            .filter(HazardTicket.result_id == result_id)
            .one_or_none()
        )

    def save(self, ticket: HazardTicket) -> HazardTicket:
        self.db.add(ticket)
        self.db.flush()
        return ticket

    def open_statuses_for_devices(self, device_ids):
        """返回每台设备未闭环隐患的最高紧迫状态。"""
        if not device_ids:
            return {}
        from src.constants.rectify_status import RECTIFIED, OPEN_HAZARD_STATUSES

        rows = (
            self.db.query(HazardTicket.device_id, HazardTicket.rectify_status)
            .filter(
                HazardTicket.device_id.in_(device_ids),
                HazardTicket.rectify_status.in_(OPEN_HAZARD_STATUSES),
            )
            .all()
        )
        priority = {RECTIFIED: 1}  # 待复验也算未闭环；有整改中的设备优先展示整改中
        result = {}
        for device_id, status in rows:
            old = result.get(device_id)
            if old is None or priority.get(status, 0) < priority.get(old, 0):
                result[device_id] = status
        return result

    def count_by_status(self):
        from sqlalchemy import func

        rows = (
            self.db.query(HazardTicket.rectify_status, func.count(HazardTicket.id))
            .group_by(HazardTicket.rectify_status)
            .all()
        )
        return {status: count for status, count in rows}

    def list_all(self):
        return self.db.query(HazardTicket).order_by(HazardTicket.id.asc()).all()

    def monthly_counts(self):
        # 报表数据量不大，按月份聚合放到 service 层做，保证 SQLite/PostgreSQL 行为一致。
        return self.list_all()


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, log: AuditLog):
        self.db.add(log)
        self.db.flush()
        return log

    def list_recent(self, limit: int = 100):
        return self.db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
