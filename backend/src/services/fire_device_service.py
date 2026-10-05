"""消防设备台账与状态重算。

设备状态不由巡检直接改写，而是按关联隐患单的流转重新计算：
- 存在未关闭隐患单 -> MAINTAINING（整改中）
- 最近一次异常结论且无未关闭隐患 -> FAULT（故障）
- 其余 -> NORMAL（正常）
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.constructors.fire_device_factory import create_fire_device_response
from src.models.entities import FireDevice, HazardTicket, InspectionResult
from src.repositories.fire_device_repository import FireDeviceRepository
from src.services.audit_service import write_audit
from src.services.errors import NotFoundError
from src.types.fire_device_payload import FireDevicePayload

OPEN_STATUSES = ("OPEN", "ASSIGNED", "RECTIFIED")


class FireDeviceService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = FireDeviceRepository(session)

    def _open_hazard_counts(self) -> dict[int, int]:
        stmt = (
            select(InspectionResult.device_id, func.count(HazardTicket.id))
            .join(HazardTicket, HazardTicket.result_id == InspectionResult.id)
            .where(HazardTicket.rectify_status.in_(OPEN_STATUSES))
            .group_by(InspectionResult.device_id)
        )
        return {device_id: count for device_id, count in self.session.execute(stmt)}

    def list(self, building_id: int | None = None) -> list[dict]:
        counts = self._open_hazard_counts()
        return [
            create_fire_device_response(device, open_hazard_count=counts.get(device.id, 0))
            for device in self.repo.find_all(building_id=building_id)
        ]

    def get(self, device_id: int) -> FireDevice:
        device = self.repo.get(device_id)
        if device is None:
            raise NotFoundError("DEVICE_NOT_FOUND")
        return device

    def create(self, payload: FireDevicePayload, actor: dict) -> dict:
        device = FireDevice(
            building_id=payload.building_id,
            device_code=payload.device_code,
            device_type=payload.device_type,
            floor=payload.floor,
            location_desc=payload.location_desc,
            install_date=payload.install_date,
            next_maintenance_at=payload.next_maintenance_at,
            status="NORMAL",
        )
        self.repo.add(device)
        write_audit(
            self.session, actor, "FireDevice.create", "FireDevice", device.id,
            f"设备登记：{device.device_code}",
        )
        self.session.commit()
        return create_fire_device_response(device)

    def recalculate_status(self, device_id: int, actor: dict | None = None) -> str:
        """根据隐患单/巡检结果重算单台设备状态并落库。"""
        device = self.get(device_id)
        open_stmt = (
            select(func.count(HazardTicket.id))
            .join(InspectionResult, HazardTicket.result_id == InspectionResult.id)
            .where(
                InspectionResult.device_id == device_id,
                HazardTicket.rectify_status.in_(OPEN_STATUSES),
            )
        )
        open_count = self.session.scalar(open_stmt) or 0
        if open_count > 0:
            new_status = "MAINTAINING"
        else:
            # 最近一条异常结论，若其隐患单已复验关闭则视为修复（NORMAL），
            # 没有隐患单或未关闭时本分支不会进入（未关闭已在上面计入 MAINTAINING）。
            latest = self.session.scalars(
                select(InspectionResult)
                .options(selectinload(InspectionResult.hazard))
                .where(InspectionResult.device_id == device_id)
                .order_by(InspectionResult.submitted_at.desc(), InspectionResult.id.desc())
                .limit(1)
            ).first()
            new_status = "FAULT" if latest is not None and latest.result_status == "ABNORMAL" and latest.hazard is None else "NORMAL"

        if device.status != new_status:
            old_status = device.status
            device.status = new_status
            self.session.flush()
            write_audit(
                self.session,
                actor,
                "FireDevice.status",
                "FireDevice",
                device.id,
                f"设备 {device.device_code} 状态重算：{old_status} -> {new_status}",
            )
        return new_status
