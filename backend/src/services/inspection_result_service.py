"""巡检结果逐项提交：版本冲突识别、并发落一份、异常自动生成隐患单。"""

import time

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src.constants.hazard_severity import DEFAULT_SEVERITY, HazardSeverity
from src.constants.user_role import ROLE_INSPECTOR
from src.constructors.inspection_result_factory import create_inspection_result_response
from src.middlewares.rbac_middleware import assert_role
from src.models.entities import HazardTicket, InspectionResult, TaskChecklistItem, utcnow
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.user_repository import UserRepository
from src.services.audit_service import write_audit
from src.services.errors import BusinessError
from src.services.fire_device_service import FireDeviceService
from src.services.inspection_task_service import InspectionTaskService
from src.types.inspection_result_payload import ResultBatchPayload, ResultItemPayload


class InspectionResultService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = InspectionResultRepository(session)
        self.task_repo = InspectionTaskRepository(session)

    @staticmethod
    def _is_lock_error(exc: OperationalError) -> bool:
        message = str(exc).lower()
        # "database is locked" 在 WAL 下有两种：普通写锁（busy_timeout 可等）
        # 与快照过期 SQLITE_BUSY_SNAPSHOT（必须结束事务重试）
        return "locked" in message or "database is locked" in message

    def _commit_with_retry(self, action, attempts: int = 8, delay: float = 0.05) -> None:
        for index in range(attempts):
            try:
                action()
                return
            except OperationalError as exc:
                self.session.rollback()
                if not self._is_lock_error(exc) or index == attempts - 1:
                    raise
                time.sleep(delay * (index + 1))

    def list(self, task_id: int | None = None, device_id: int | None = None) -> list[dict]:
        results = self.repo.find_all(task_id=task_id, device_id=device_id)
        device_repo = FireDeviceRepository(self.session)
        user_repo = UserRepository(self.session)
        tasks = {t.id: t for t in self.task_repo.find_all()}
        devices = {d.id: d for d in device_repo.find_all()}
        users = {u.id: u.name for u in user_repo.find_all()}
        rows = []
        for result in results:
            task = tasks.get(result.task_id)
            item_name = ""
            building_name = ""
            if task is not None:
                item = next((i for i in task.items if i.item_code == result.item_code), None)
                item_name = item.item_name if item else ""
                building_name = task.building.name if task.building else ""
            device = devices.get(result.device_id)
            rows.append(
                create_inspection_result_response(
                    result,
                    item_name=item_name,
                    device_code=device.device_code if device else "",
                    building_name=building_name,
                    submitter_name=users.get(result.submitted_by, ""),
                )
            )
        return rows

    def batch_submit(self, task_id: int, payload: ResultBatchPayload, actor: dict) -> dict:
        """逐项提交：版本过期/并发冲突的单项拒绝，其余正常保存。

        SQLite WAL 在并发下可能出现快照过期型 SQLITE_BUSY，整体回滚后重试整批；
        PostgreSQL 由行锁串行化，不会走到该重试。
        """
        last_lock: OperationalError | None = None
        for attempt in range(6):
            try:
                return self._batch_submit_once(task_id, payload, actor)
            except OperationalError as exc:
                self.session.rollback()
                if not self._is_lock_error(exc) or attempt == 5:
                    raise
                last_lock = exc
                time.sleep(0.03 * (attempt + 1))
        if last_lock:
            raise last_lock

    def _batch_submit_once(self, task_id: int, payload: ResultBatchPayload, actor: dict) -> dict:
        assert_role(actor, ROLE_INSPECTOR)
        task_service = InspectionTaskService(self.session)
        task = task_service.get(task_id)
        task_service.require_editable(task, actor)

        items_by_code: dict[str, TaskChecklistItem] = {i.item_code: i for i in task.items}
        saved: list[dict] = []
        conflicts: list[dict] = []
        affected_devices: set[int] = set()

        for entry in payload.items:
            outcome, device_id = self._submit_one_with_retry(
                task, items_by_code, entry, actor
            )
            if outcome is not None:
                saved.append(outcome)
                if device_id is not None:
                    affected_devices.add(device_id)
            else:
                # _submit_one_with_retry 在失败时已把冲突记录写入 conflicts
                conflicts.extend(self._last_conflicts)

        # 异常项生成隐患单后，受影响设备状态立即重算（统一在末尾事务提交）
        device_service = FireDeviceService(self.session)
        for device_id in affected_devices:
            device_service.recalculate_status(device_id, actor)

        abnormal_count = sum(1 for s in saved if s["result_status"] == "ABNORMAL")
        write_audit(
            self.session,
            actor,
            "InspectionResult.batch_submit",
            "InspectionTask",
            task_id,
            f"逐项提交 {len(saved)} 项，冲突 {len(conflicts)} 项，异常 {abnormal_count} 项",
        )
        # SQLite 并发写时 commit 可能短暂加锁；事务整体重试（无外部副作用，幂等）
        self._commit_with_retry(self.session.commit)
        return {
            "task_id": task_id,
            "saved": saved,
            "conflicts": conflicts,
            "task": task_service.detail(task_id),
        }

    def _submit_one_with_retry(
        self,
        task,
        items_by_code: dict[str, TaskChecklistItem],
        entry: ResultItemPayload,
        actor: dict,
        attempts: int = 6,
    ) -> tuple[dict | None, int | None]:
        self._last_conflicts: list[dict] = []
        for index in range(attempts):
            sp = self.session.begin_nested()
            try:
                return self._process_item(task, items_by_code, entry, actor)
            except BusinessError as exc:
                sp.rollback()
                self._last_conflicts = [
                    {"item_code": entry.item_code, "code": exc.code, "message": exc.message}
                ]
                return None, None
            except IntegrityError:
                sp.rollback()
                self._last_conflicts = [
                    {
                        "item_code": entry.item_code,
                        "code": "CONCURRENT_SUBMISSION",
                        "message": f"检查项 {entry.item_code} 已由其他巡检员提交，同一任务只保留一份结果",
                    }
                ]
                return None, None
            except OperationalError as exc:
                sp.rollback()
                if not self._is_lock_error(exc) or index == attempts - 1:
                    self._last_conflicts = [
                        {
                            "item_code": entry.item_code,
                            "code": "RATE_LIMITED",
                            "message": "系统繁忙，检查项暂未保存，请稍后重试",
                        }
                    ]
                    return None, None
                time.sleep(0.05 * (index + 1))
        return None, None

    def _process_item(
        self,
        task,
        items_by_code: dict[str, TaskChecklistItem],
        entry: ResultItemPayload,
        actor: dict,
    ) -> tuple[dict, int]:
        item = items_by_code.get(entry.item_code)
        if item is None:
            raise BusinessError(
                "CHECKLIST_ITEM_NOT_FOUND",
                f"检查项 {entry.item_code} 不属于该巡检任务",
                status_code=404,
            )
        if entry.checklist_version != task.checklist_version or \
                item.checklist_version != task.checklist_version:
            # 清单版本过期：拒绝旧项并明确说明当前版本冲突
            raise BusinessError(
                "CHECKLIST_VERSION_CONFLICT",
                (
                    f"检查项 {entry.item_code} 使用的清单版本 v{entry.checklist_version}"
                    f" 已过期，当前为 v{task.checklist_version}，请刷新清单后重新提交"
                ),
                status_code=409,
            )

        existing = self.repo.find_by_task_item(task.id, entry.item_code)
        if existing is not None and existing.submitted_by != actor["id"]:
            # 两名巡检员并发提交同一任务：唯一一份结果，后到者拒绝
            raise BusinessError(
                "CONCURRENT_SUBMISSION",
                f"检查项 {entry.item_code} 已由其他巡检员提交，同一任务只保留一份结果",
                status_code=409,
            )

        if existing is None:
            result = InspectionResult(
                task_id=task.id,
                device_id=item.device_id,
                item_code=entry.item_code,
                result_status=entry.result_status,
                measured_value=entry.measured_value,
                photo_url=entry.photo_url,
                note=entry.note,
                submitted_by=actor["id"],
            )
            self.repo.add(result)
        else:
            # 同一巡检员对自己结果的修正提交（任务仍处于巡检中）
            result = existing
            result.result_status = entry.result_status
            result.measured_value = entry.measured_value
            result.photo_url = entry.photo_url
            result.note = entry.note

        self.session.flush()
        self._sync_hazard(result, entry.severity, entry.result_status, actor)
        return (
            {
                "item_code": entry.item_code,
                "result_id": result.id,
                "result_status": result.result_status,
                "hazard_id": result.hazard.id if result.hazard else None,
            },
            result.device_id,
        )

    def _sync_hazard(
        self,
        result: InspectionResult,
        submitted_severity: str | None,
        result_status: str,
        actor: dict,
    ) -> None:
        """异常结果生成/复用隐患单；改回正常则关闭未整改的隐患单。"""
        if result_status == "ABNORMAL":
            severity = submitted_severity if submitted_severity in HazardSeverity else DEFAULT_SEVERITY
            if result.hazard is None:
                ticket = HazardTicket(
                    result=result,
                    severity=severity,
                    rectify_status="OPEN",
                )
                self.session.add(ticket)
                self.session.flush()
                write_audit(
                    self.session,
                    actor,
                    "HazardTicket.create",
                    "HazardTicket",
                    ticket.id,
                    f"巡检异常自动生成隐患单：检查项 {result.item_code}，级别 {severity}",
                )
            elif submitted_severity in HazardSeverity:
                result.hazard.severity = severity
        elif result.hazard is not None and result.hazard.rectify_status == "OPEN":
            # 巡检员在整改开始前把结论修正为正常，隐患单作废关闭
            result.hazard.rectify_status = "CLOSED"
            result.hazard.closed_by = actor["id"]
            result.hazard.closed_at = utcnow()
            result.hazard.rectify_note = (result.hazard.rectify_note + " / 巡检员复核正常，自动关闭").strip(" /")
