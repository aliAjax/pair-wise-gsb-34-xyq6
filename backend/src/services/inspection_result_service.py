from datetime import datetime

from sqlalchemy.orm import Session

from src.constants.device_status import FAULT
from src.constants.hazard_severity import DEFAULT_SEVERITY
from src.constants.inspection_status import (
    CLOSED_TASK_STATUSES,
    IN_PROGRESS,
    SUBMITTED,
)
from src.constants.rectify_status import OPEN
from src.constants.result_status import RESULT_ABNORMAL
from src.models.hazard_ticket import HazardTicket
from src.models.inspection_result import InspectionResult
from src.models.inspection_task import InspectionTask
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import (
    InspectionResultRepository,
    ResultConflictError,
)
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.services.audit_service import write_audit_log
from src.services.errors import ConflictError
from src.services.inspection_task_service import InspectionTaskService


class InspectionResultService:
    def __init__(self, db: Session):
        self.db = db
        self.result_repo = InspectionResultRepository(db)
        self.task_repo = InspectionTaskRepository(db)
        self.ticket_repo = HazardTicketRepository(db)
        self.device_repo = FireDeviceRepository(db)
        self.task_service = InspectionTaskService(db)

    def list(self, task_id: int | None = None, device_id: int | None = None):
        return self.result_repo.find_all(task_id=task_id, device_id=device_id)

    def submit(self, task_id: int, payload, actor: dict) -> dict:
        task = self.task_service.get(task_id)

        # 1) 角色归属：只有领取该任务的巡检员本人可以提交。
        if task.inspector_id != actor["id"]:
            if task.inspector_id is None:
                raise ConflictError("TASK_NOT_CLAIMABLE", "任务尚未领取，请先领取后再提交结果")
            raise ConflictError("TASK_NOT_OWNED", "只有领取该任务的巡检员才能提交结果")

        # 2) 并发互斥：任务一旦进入终态，后续提交全部拒绝（两名巡检员同时提交只落一份）。
        if task.status in CLOSED_TASK_STATUSES:
            write_audit_log(
                self.db,
                actor=actor["username"],
                entity="InspectionResult",
                event="InspectionResult.duplicate",
                target_type="InspectionTask",
                target_id=task_id,
                task_id=task_id,
            )
            self.db.commit()
            raise ConflictError("TASK_CLOSED", "巡检任务已提交/复核，结果不可再变更")

        # 3) 行锁串行化：同任务的并发提交在 PostgreSQL 上只放一个事务进入写入区，
        #    SQLite 写事务天然串行；终态任务在锁后复查，保证两名巡检员只落一份结果。
        locked_task = (
            self.db.query(InspectionTask)
            .filter(InspectionTask.id == task_id)
            .with_for_update()
            .first()
        )
        if locked_task is not None and locked_task.status in CLOSED_TASK_STATUSES:
            self.db.rollback()
            raise ConflictError("RESULT_DUPLICATED", "该巡检任务已有一份提交结果，重复提交已被拒绝")

        current_version = task.checklist_version
        stale = payload.checklist_version != current_version

        saved = []
        rejected = []
        abnormal_count = 0
        normal_count = 0

        # 当前已保存结果（同批次/历史批次逐项覆盖，保证一项只落一份）。
        existing = {row.item_code: row for row in self.result_repo.list_by_task(task_id)}
        active_items = {row.item_code: row for row in self.task_repo.active_checklist_items(task_id)}

        for item in payload.items:
            checklist_item = self.task_repo.get_checklist_item(task_id, item.item_code)
            # 4) 清单版本冲突判定。
            if checklist_item is None:
                rejected.append(self._reject(item.item_code, item.device_id, "CHECKLIST_ITEM_UNKNOWN",
                                             f"检查项 {item.item_code} 不属于当前清单 {current_version}"))
                continue
            if checklist_item.deprecated:
                rejected.append(self._reject(
                    item.item_code, item.device_id, "CHECKLIST_STALE",
                    f"检查项 {item.item_code} 已在新版本清单中移除（你的版本 {payload.checklist_version}，当前版本 {current_version}），请刷新清单",
                ))
                write_audit_log(
                    self.db,
                    actor=actor["username"],
                    entity="InspectionResult",
                    event="InspectionResult.stale",
                    target_type="InspectionResult",
                    target_id=f"{task_id}:{item.item_code}",
                    task_id=task_id,
                    item_code=item.item_code,
                    client_version=payload.checklist_version,
                    current_version=current_version,
                )
                continue
            if stale:
                # 版本过期时：旧项里在新清单仍存在的照存，但整批标记冲突，要求补齐新增项。
                pass

            if item.device_id is not None and not self.device_repo.get(item.device_id):
                rejected.append(self._reject(item.item_code, item.device_id, "NOT_FOUND",
                                             f"设备 {item.device_id} 不存在"))
                continue

            result = existing.get(item.item_code)
            if result is None:
                result = InspectionResult(
                    task_id=task_id,
                    device_id=item.device_id,
                    item_code=item.item_code,
                    result_status=item.result_status,
                    measured_value=item.measured_value,
                    photo_url=item.photo_url,
                    note=item.note,
                    checklist_version=current_version,
                )
                try:
                    self.result_repo.save(result)
                except ResultConflictError:
                    self.db.rollback()
                    raise ConflictError("RESULT_DUPLICATED", "检查项结果已存在，重复提交已被拒绝")
            else:
                result.device_id = item.device_id
                result.result_status = item.result_status
                result.measured_value = item.measured_value
                result.photo_url = item.photo_url
                result.note = item.note
                result.checklist_version = current_version
                self.db.flush()

            saved.append({
                "item_code": result.item_code,
                "device_id": result.device_id,
                "result_status": result.result_status,
            })
            write_audit_log(
                self.db,
                actor=actor["username"],
                entity="InspectionResult",
                event="InspectionResult.submit",
                target_type="InspectionResult",
                target_id=result.id or f"{task_id}:{result.item_code}",
                task_id=task_id,
                device_id=result.device_id,
                item_code=result.item_code,
                result_status=result.result_status,
            )

            # 5) 异常结果 -> 隐患单（一个结果最多一张），设备立即转为故障。
            if result.result_status == RESULT_ABNORMAL:
                abnormal_count += 1
                ticket = self.ticket_repo.get_by_result(result.id)
                if ticket is None:
                    ticket = HazardTicket(
                        result_id=result.id,
                        device_id=result.device_id,
                        severity=DEFAULT_SEVERITY,
                        owner_id=None,
                        deadline=None,
                        rectify_status=OPEN,
                        rectify_note=None,
                        closed_at=None,
                    )
                    self.ticket_repo.save(ticket)
                    write_audit_log(
                        self.db,
                        actor=actor["username"],
                        entity="HazardTicket",
                        event="HazardTicket.create",
                        target_type="HazardTicket",
                        target_id=ticket.id,
                        result_id=result.id,
                        ticket_id=ticket.id,
                        severity=DEFAULT_SEVERITY,
                    )
                device = self.device_repo.get(result.device_id)
                if device and device.status != FAULT:
                    device.status = FAULT
                    self.db.flush()
                    write_audit_log(
                        self.db,
                        actor=actor["username"],
                        entity="FireDevice",
                        event="FireDevice.status",
                        target_type="FireDevice",
                        target_id=device.id,
                        device_id=device.id,
                        status=FAULT,
                    )
            else:
                normal_count += 1

        if stale:
            missing_new = [code for code in active_items if code not in {s["item_code"] for s in saved}]
            for code in missing_new:
                rejected.append(self._reject(
                    code, None, "CHECKLIST_STALE",
                    f"清单版本已过期：新增检查项 {code} 未提交（你的版本 {payload.checklist_version}，当前版本 {current_version}），请刷新清单补检",
                ))

        # 6) 有效检查项全部提交完后任务进入待复验；否则保持巡检中允许继续补录。
        filled_codes = {row.item_code for row in self.result_repo.list_by_task(task_id)}
        all_filled = all(code in filled_codes for code in active_items)
        task_status_after = SUBMITTED if all_filled else IN_PROGRESS
        finished_at = datetime.now() if all_filled else None
        self.db.query(InspectionTask).filter(InspectionTask.id == task_id).update(
            {InspectionTask.status: task_status_after, InspectionTask.finished_at: finished_at}
        )
        self.db.flush()

        if all_filled and not rejected:
            write_audit_log(
                self.db,
                actor=actor["username"],
                entity="InspectionTask",
                event="InspectionTask.submit",
                target_type="InspectionTask",
                target_id=task_id,
                task_id=task_id,
                normal_count=normal_count,
                abnormal_count=abnormal_count,
            )

        self.db.commit()

        return {
            "task_id": task_id,
            "task_status": task_status_after,
            "checklist_version": payload.checklist_version,
            "current_version": current_version,
            "stale": stale or any(row["reason_code"] == "CHECKLIST_STALE" for row in rejected),
            "saved": saved,
            "rejected": rejected,
            "all_items_completed": all_filled,
        }

    @staticmethod
    def _reject(item_code: str, device_id: int | None, reason_code: str, reason: str) -> dict:
        return {"item_code": item_code, "device_id": device_id, "reason_code": reason_code, "reason": reason}
