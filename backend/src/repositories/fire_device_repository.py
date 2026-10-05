from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import FireDevice


class FireDeviceRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self, building_id: int | None = None) -> list[FireDevice]:
        stmt = select(FireDevice).order_by(FireDevice.building_id, FireDevice.id)
        if building_id is not None:
            stmt = stmt.where(FireDevice.building_id == building_id)
        return list(self.session.scalars(stmt))

    def get(self, device_id: int) -> FireDevice | None:
        return self.session.get(FireDevice, device_id)

    def add(self, device: FireDevice) -> FireDevice:
        self.session.add(device)
        self.session.flush()
        return device
