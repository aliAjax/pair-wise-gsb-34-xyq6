from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from src.db.session import Base


class HazardTicket(Base):
    __tablename__ = "hazard_ticket"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, nullable=False, unique=True, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    severity = Column(String(16), nullable=False, default="MEDIUM")
    owner_id = Column(Integer, nullable=True, index=True)
    deadline = Column(Date, nullable=True)
    rectify_status = Column(String(16), nullable=False, default="OPEN", index=True)
    rectify_note = Column(Text, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor = Column(String(64), nullable=False)
    action = Column(String(128), nullable=False)
    target_type = Column(String(32), nullable=False)
    target_id = Column(String(32), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
