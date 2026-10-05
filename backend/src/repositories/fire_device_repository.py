from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.fire_device import FireDevice


class FireDeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self, building_id: int | None = None):
        query = self.db.query(FireDevice)
        if building_id is not None:
            query = query.filter(FireDevice.building_id == building_id)
        return query.order_by(FireDevice.building_id.asc(), FireDevice.floor.asc(), FireDevice.id.asc()).all()

    def get(self, device_id: int) -> FireDevice | None:
        return self.db.get(FireDevice, device_id)

    def list_by_ids(self, device_ids):
        if not device_ids:
            return []
        return self.db.query(FireDevice).filter(FireDevice.id.in_(device_ids)).all()

    def status_distribution(self):
        rows = (
            self.db.query(FireDevice.status, func.count(FireDevice.id))
            .group_by(FireDevice.status)
            .all()
        )
        return {status: count for status, count in rows}

    def save(self, device: FireDevice) -> FireDevice:
        self.db.add(device)
        self.db.flush()
        return device
