from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from src.db.session import Base


class InspectionResult(Base):
    __tablename__ = "inspection_result"
    __table_args__ = (
        # 同一任务同一检查项只能落一份结果：并发提交的数据库兜底。
        UniqueConstraint("task_id", "item_code", name="uq_result_task_item"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    item_code = Column(String(64), nullable=False)
    result_status = Column(String(16), nullable=False)
    measured_value = Column(String(128), nullable=True)
    photo_url = Column(String(256), nullable=True)
    note = Column(Text, nullable=True)
    checklist_version = Column(String(16), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
