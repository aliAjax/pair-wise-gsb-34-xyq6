from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from src.db.session import Base


class InspectionTask(Base):
    __tablename__ = "inspection_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(Integer, nullable=False, index=True)
    inspector_id = Column(Integer, nullable=True, index=True)
    plan_date = Column(String(32), nullable=False)
    task_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="PLANNED", index=True)
    checklist_version = Column(String(16), nullable=False, default="v1")
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class ChecklistItem(Base):
    """任务创建时从清单模板快照下来的检查项；deprecated 标记版本升级后新增清单中已移除的旧项。"""

    __tablename__ = "checklist_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    item_code = Column(String(64), nullable=False)
    item_name = Column(String(128), nullable=False)
    checklist_version = Column(String(16), nullable=False)
    deprecated = Column(Boolean, nullable=False, default=False)


class ChecklistTemplate(Base):
    """按设备类型维护的清单模板，每个 (task_type, version, item_code) 唯一。"""

    __tablename__ = "checklist_template"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(32), nullable=False, index=True)
    version = Column(String(16), nullable=False)
    item_code = Column(String(64), nullable=False)
    item_name = Column(String(128), nullable=False)
