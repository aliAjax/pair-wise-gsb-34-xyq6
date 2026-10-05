"""消防设备状态重算：隐患闭环后由设备未闭环隐患反推状态，总览依赖同一口径。"""
from sqlalchemy.orm import Session

from src.constants.device_status import FAULT, MAINTAINING, NORMAL
from src.constants.rectify_status import ASSIGNED, RECTIFIED, REJECTED
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository

# 隐患状态 -> 设备应呈现的状态
TICKET_STATUS_TO_DEVICE = {
    "OPEN": FAULT,          # 待派单：设备带病
    ASSIGNED: MAINTAINING,
    REJECTED: MAINTAINING,
    RECTIFIED: FAULT,       # 已整改待复验，设备仍带病
}


class DeviceStatusRecalculator:
    def __init__(self, db: Session):
        self.db = db
        self.device_repo = FireDeviceRepository(db)
        self.ticket_repo = HazardTicketRepository(db)

    def recalculate(self, device_id: int):
        device = self.device_repo.get(device_id)
        if not device:
            return None
        open_tickets = [
            ticket
            for ticket in self.ticket_repo.find_all(device_id=device_id)
            if ticket.rectify_status in TICKET_STATUS_TO_DEVICE
        ]
        if not open_tickets:
            new_status = NORMAL
        else:
            # 只要存在待整改/退回单，设备就是整改中；否则处于待复验的故障态。
            new_status = NORMAL
            for ticket in open_tickets:
                mapped = TICKET_STATUS_TO_DEVICE[ticket.rectify_status]
                if mapped == MAINTAINING:
                    new_status = MAINTAINING
                    break
                new_status = FAULT
        if device.status != new_status:
            device.status = new_status
            self.db.flush()
        return device
