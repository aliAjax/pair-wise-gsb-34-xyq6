from datetime import date

from sqlalchemy.orm import Session

from src.constants.device_status import DeviceStatus
from src.models.fire_device import FireDevice
from src.repositories.fire_device_repository import FireDeviceRepository
from src.services.errors import NotFoundError, ServiceError


class FireDeviceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FireDeviceRepository(db)

    def list(self, building_id: int | None = None):
        return self.repo.find_all(building_id=building_id)

    def get(self, device_id: int) -> FireDevice:
        device = self.repo.get(device_id)
        if not device:
            raise NotFoundError("消防设备不存在")
        return device

    def create(self, payload) -> FireDevice:
        device = FireDevice(
            building_id=payload.building_id,
            device_code=payload.device_code,
            device_type=payload.device_type,
            floor=payload.floor,
            location_desc=payload.location_desc,
            install_date=date.fromisoformat(payload.install_date) if payload.install_date else None,
            next_maintenance_at=date.fromisoformat(payload.next_maintenance_at) if payload.next_maintenance_at else None,
            status="NORMAL",
        )
        return self.repo.save(device)

    def status_distribution(self):
        return self.repo.status_distribution()

    def mark_status(self, device_id: int, status: str) -> FireDevice:
        if status not in DeviceStatus:
            raise ServiceError("VALIDATION_FAILED", f"未知设备状态：{status}")
        device = self.get(device_id)
        device.status = status
        self.db.flush()
        return device
