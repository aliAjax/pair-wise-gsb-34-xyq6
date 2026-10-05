from sqlalchemy import Column, Date, Integer, String

from src.db.session import Base


class FireDevice(Base):
    __tablename__ = "fire_device"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(Integer, nullable=False, index=True)
    device_code = Column(String(64), nullable=False, unique=True)
    device_type = Column(String(32), nullable=False)
    floor = Column(String(16), nullable=False)
    location_desc = Column(String(128), nullable=False)
    install_date = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, default="NORMAL", index=True)
    next_maintenance_at = Column(Date, nullable=True)
