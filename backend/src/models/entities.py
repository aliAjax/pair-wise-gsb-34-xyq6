"""SQLAlchemy ORM 模型（持久层），与 Pydantic 传输 DTO 分离。"""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    # SQLite 不保留 tzinfo，统一使用 naive UTC 以保证比较与查询一致
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "app_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)

    buildings: Mapped[list["Building"]] = relationship(back_populates="manager")
    claimed_tasks: Mapped[list["InspectionTask"]] = relationship(back_populates="inspector")


class Building(Base):
    __tablename__ = "building"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    campus: Mapped[str] = mapped_column(String(128), nullable=False)
    floor_count: Mapped[int] = mapped_column(Integer, default=1)
    fire_grade: Mapped[str] = mapped_column(String(32), default="二级")
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"), nullable=True)
    address_code: Mapped[str] = mapped_column(String(64), default="")

    manager: Mapped["User | None"] = relationship(back_populates="buildings")
    devices: Mapped[list["FireDevice"]] = relationship(back_populates="building")
    tasks: Mapped[list["InspectionTask"]] = relationship(back_populates="building")


class FireDevice(Base):
    __tablename__ = "fire_device"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("building.id"), nullable=False)
    device_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String(32), nullable=False)
    floor: Mapped[str] = mapped_column(String(16), default="1")
    location_desc: Mapped[str] = mapped_column(String(255), default="")
    install_date: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    status: Mapped[str] = mapped_column(String(32), default="NORMAL")
    next_maintenance_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    building: Mapped["Building"] = relationship(back_populates="devices")


class InspectionTask(Base):
    __tablename__ = "inspection_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("building.id"), nullable=False)
    inspector_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"), nullable=True)
    plan_date: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PLANNED")
    checklist_version: Mapped[int] = mapped_column(Integer, default=1)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    building: Mapped["Building"] = relationship(back_populates="tasks")
    inspector: Mapped["User | None"] = relationship(back_populates="claimed_tasks")
    items: Mapped[list["TaskChecklistItem"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )
    results: Mapped[list["InspectionResult"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class TaskChecklistItem(Base):
    """任务快照清单：任务创建时按设备类型生成，随清单版本升级。"""

    __tablename__ = "task_checklist_item"
    __table_args__ = (
        UniqueConstraint("task_id", "item_code", name="uq_task_item"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("inspection_task.id"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("fire_device.id"), nullable=False)
    item_code: Mapped[str] = mapped_column(String(64), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    checklist_version: Mapped[int] = mapped_column(Integer, default=1)

    task: Mapped["InspectionTask"] = relationship(back_populates="items")


class InspectionResult(Base):
    __tablename__ = "inspection_result"
    __table_args__ = (
        # 同一任务同一检查项全局唯一：两名巡检员并发提交只落一份
        UniqueConstraint("task_id", "item_code", name="uq_result_task_item"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("inspection_task.id"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("fire_device.id"), nullable=False)
    item_code: Mapped[str] = mapped_column(String(64), nullable=False)
    result_status: Mapped[str] = mapped_column(String(16), nullable=False)
    measured_value: Mapped[str] = mapped_column(String(255), default="")
    photo_url: Mapped[str] = mapped_column(String(255), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    submitted_by: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    task: Mapped["InspectionTask"] = relationship(back_populates="results")
    hazard: Mapped["HazardTicket | None"] = relationship(
        back_populates="result", uselist=False, cascade="all, delete-orphan"
    )


class HazardTicket(Base):
    __tablename__ = "hazard_ticket"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result_id: Mapped[int] = mapped_column(
        ForeignKey("inspection_result.id"), unique=True, nullable=False
    )
    severity: Mapped[str] = mapped_column(String(16), default="MEDIUM")
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rectify_status: Mapped[str] = mapped_column(String(16), default="OPEN")
    rectify_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    rectified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_by: Mapped[int | None] = mapped_column(ForeignKey("app_user.id"), nullable=True)

    result: Mapped["InspectionResult"] = relationship(back_populates="hazard")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor_name: Mapped[str] = mapped_column(String(64), default="")
    actor_role: Mapped[str] = mapped_column(String(32), default="")
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), default="")
    target_id: Mapped[str] = mapped_column(String(64), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
