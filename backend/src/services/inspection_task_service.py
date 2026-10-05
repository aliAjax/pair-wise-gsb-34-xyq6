"""巡检任务排期、领取、提交复核、复验关闭与清单版本管理。"""

from sqlalchemy import update
from sqlalchemy.orm import Session

from src.constructors.inspection_task_factory import create_inspection_task_response
from src.constants.device_type import DEVICE_CHECKLIST
from src.middlewares.rbac_middleware import assert_role
from src.constants.user_role import ROLE_INSPECTOR, ROLE_SUPERVISOR
from src.models.entities import InspectionTask, TaskChecklistItem, utcnow
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.user_repository import UserRepository
from src.services.audit_service import write_audit
from src.services.errors import ConflictError, NotFoundError
from src.types.inspection_task_payload import InspectionTaskPayload

_EDITABLE_STATUSES = ("IN_PROGRESS",)


class InspectionTaskService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = InspectionTaskRepository(session)
        self.user_repo = UserRepository(session)
        self.device_repo = FireDeviceRepository(session)

    # ---------- 查询 ----------

    def _refresh_overdue(self) -> None:
        """计划日期已过完整自然日仍待领取的任务自动置为 OVERDUE（幂等）。"""
        start_of_today = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = self.session.execute(
            update(InspectionTask)
            .where(InspectionTask.status == "PLANNED", InspectionTask.plan_date < start_of_today)
            .values(status="OVERDUE")
        )
        if result.rowcount:
            self.session.commit()

    def list(self, building_id: int | None = None, status: str | None = None) -> list[dict]:
        self._refresh_overdue()
        tasks = self.repo.find_all(building_id=building_id, status=status)
        return [self._to_dto(task) for task in tasks]

    def get(self, task_id: int) -> InspectionTask:
        task = self.repo.get(task_id)
        if task is None:
            raise NotFoundError("TASK_NOT_FOUND")
        return task

    def detail(self, task_id: int) -> dict:
        return self._to_dto(self.get(task_id))

    def _to_dto(self, task: InspectionTask) -> dict:
        submitter_names = {
            u.id: u.name for u in self.user_repo.find_all()
        }
        dto = create_inspection_task_response(task)
        for item in dto["items"]:
            if item["submitted_by"] is not None:
                item["submitted_by_name"] = submitter_names.get(item["submitted_by"], "")
        return dto

    # ---------- 写动作 ----------

    def create(self, payload: InspectionTaskPayload, actor: dict) -> dict:
        assert_role(actor, ROLE_SUPERVISOR)
        from src.services.building_service import BuildingService

        building = BuildingService(self.session).require(payload.building_id)
        if payload.task_type not in DEVICE_CHECKLIST:
            raise self._validation("task_type 必须是受支持的消防设备类型")

        devices = [
            d for d in self.device_repo.find_all(building_id=building.id)
            if d.device_type == payload.task_type
        ]
        if not devices:
            return self._validation("该楼栋下没有此类设备，无法排期巡检")

        task = InspectionTask(
            building_id=building.id,
            plan_date=payload.plan_date or utcnow(),
            task_type=payload.task_type,
            status="PLANNED",
            checklist_version=1,
        )
        self.repo.add(task)
        for device in devices:
            for item_code, item_name in DEVICE_CHECKLIST[payload.task_type]:
                self.session.add(
                    TaskChecklistItem(
                        task_id=task.id,
                        device_id=device.id,
                        item_code=f"{device.id}-{item_code}",
                        item_name=item_name,
                        checklist_version=1,
                    )
                )
        self.session.flush()
        write_audit(
            self.session, actor, "InspectionTask.create", "InspectionTask", task.id,
            f"按楼栋排期：{building.name} / {payload.task_type}，共 {len(devices)} 台设备",
        )
        self.session.commit()
        return self.detail(task.id)

    @staticmethod
    def _validation(message: str):
        from src.services.errors import BusinessError

        return BusinessError("VALIDATION_FAILED", message=message, status_code=422)

    def claim(self, task_id: int, actor: dict) -> dict:
        """巡检员按楼栋领取：条件更新保证并发下只有一人领取成功。"""
        assert_role(actor, ROLE_INSPECTOR)
        self._refresh_overdue()
        task = self.get(task_id)
        result = self.session.execute(
            update(InspectionTask)
            .where(InspectionTask.id == task_id, InspectionTask.status == "PLANNED")
            .values(inspector_id=actor["id"], status="IN_PROGRESS")
        )
        if result.rowcount == 0:
            self.session.rollback()
            raise ConflictError("TASK_NOT_CLAIMABLE")
        write_audit(
            self.session, actor, "InspectionTask.claim", "InspectionTask", task_id,
            f"巡检员领取巡检任务 #{task_id}",
        )
        self.session.commit()
        return self.detail(task_id)

    def bump_checklist_version(self, task_id: int, actor: dict) -> dict:
        """主管升级清单版本：所有检查项带上新版本，巡检员旧表单立即过期。"""
        assert_role(actor, ROLE_SUPERVISOR)
        task = self.get(task_id)
        task.checklist_version += 1
        for item in task.items:
            item.checklist_version = task.checklist_version
        write_audit(
            self.session, actor, "InspectionTask.bump_version", "InspectionTask", task_id,
            f"巡检清单升级到 v{task.checklist_version}，旧版本提交将被拒绝",
        )
        self.session.commit()
        return self.detail(task_id)

    def require_editable(self, task: InspectionTask, actor: dict) -> None:
        if task.status not in _EDITABLE_STATUSES:
            raise ConflictError("TASK_NOT_EDITABLE")
        if task.inspector_id != actor["id"]:
            # 只有领取该任务的巡检员能提交；并发冒领也无法写入第二份结果
            from src.services.errors import RbacDeniedError

            raise RbacDeniedError()

    def submit_for_review(self, task_id: int, actor: dict) -> dict:
        """巡检员完成全部检查项后提交复核。"""
        assert_role(actor, ROLE_INSPECTOR)
        task = self.get(task_id)
        self.require_editable(task, actor)
        submitted_codes = {r.item_code for r in task.results}
        remaining = [i.item_code for i in task.items if i.item_code not in submitted_codes]
        if remaining:
            raise ConflictError("TASK_INCOMPLETE", remaining=len(remaining))
        task.status = "SUBMITTED"
        task.finished_at = utcnow()
        write_audit(
            self.session, actor, "InspectionTask.submit", "InspectionTask", task_id,
            f"巡检任务 #{task_id} 全部检查项完成，提交复验",
        )
        self.session.commit()
        return self.detail(task_id)

    def review(self, task_id: int, note: str, actor: dict) -> dict:
        """主管复验关闭巡检任务（隐患单的复验关闭在隐患流程中独立进行）。"""
        assert_role(actor, ROLE_SUPERVISOR)
        task = self.get(task_id)
        if task.status != "SUBMITTED":
            raise ConflictError("TASK_NOT_REVIEWABLE")
        task.status = "REVIEWED"
        task.reviewed_at = utcnow()
        write_audit(
            self.session, actor, "InspectionTask.review", "InspectionTask", task_id,
            f"巡检任务复验关闭：{note or '合格'}",
        )
        self.session.commit()
        return self.detail(task_id)
