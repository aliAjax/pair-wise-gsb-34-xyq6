from datetime import date

from sqlalchemy.orm import Session

from src.constants.inspection_status import (
    CLOSED_TASK_STATUSES,
    IN_PROGRESS,
    PLANNED,
    REVIEWED,
    SUBMITTED,
)
from src.models.inspection_task import ChecklistItem, ChecklistTemplate, InspectionTask
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.services.audit_service import write_audit_log
from src.services.errors import ConflictError, NotFoundError, ServiceError

# 每个设备类型的初始清单（v1）。
INITIAL_CHECKLISTS = {
    "EXTINGUISHER": [
        ("EXT_PRESSURE", "压力指针在绿区"),
        ("EXT_QUALITY", "瓶身无锈蚀、铅封完好"),
        ("EXT_EXPIRE", "在有效期内"),
    ],
    "HYDRANT": [
        ("HYD_WATER", "水压正常、阀门可开启"),
        ("HYD_BOX", "消火栓箱内水带水枪齐全"),
        ("HYD_SEAL", "接口无锈蚀渗漏"),
    ],
    "SMOKE_DETECTOR": [
        ("SD_TEST", "烟感自检灯闪烁正常"),
        ("SD_DUST", "探头无积灰遮挡"),
    ],
    "SPRINKLER": [
        ("SP_HEAD", "喷淋头无破损、无遮挡"),
        ("SP_PIPE", "管网压力正常无渗漏"),
    ],
    "EXIT_LIGHT": [
        ("EL_LIGHT", "疏散指示灯常亮"),
        ("EL_BATTERY", "应急电池断电续航合格"),
    ],
}


class InspectionTaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InspectionTaskRepository(db)
        self.result_repo = InspectionResultRepository(db)

    # ---------- 查询 ----------
    def list(self, building_id: int | None = None, status: str | None = None):
        return self.repo.find_all(building_id=building_id, status=status)

    def get(self, task_id: int) -> InspectionTask:
        task = self.repo.get(task_id)
        if not task:
            raise NotFoundError("巡检任务不存在")
        return task

    def checklist(self, task_id: int):
        task = self.get(task_id)
        items = self.repo.list_checklist_items(task_id)
        results = {row.item_code: row for row in self.result_repo.list_by_task(task_id)}
        from src.constructors.inspection_task_factory import build_checklist_item_response, build_inspection_task_response

        return {
            "task": build_inspection_task_response(task),
            "current_version": task.checklist_version,
            "items": [build_checklist_item_response(item, results.get(item.item_code)) for item in items],
        }

    # ---------- 排期创建（主管） ----------
    def create_task(self, payload, actor: dict) -> InspectionTask:
        if payload.task_type not in INITIAL_CHECKLISTS:
            raise ServiceError("VALIDATION_FAILED", "未知的巡检设备类型")
        latest = self.repo.latest_template_version(payload.task_type) or "v1"
        task = InspectionTask(
            building_id=payload.building_id,
            inspector_id=None,
            plan_date=payload.plan_date,
            task_type=payload.task_type,
            status=PLANNED,
            checklist_version=latest,
        )
        self.repo.save(task)
        template = self.repo.list_template(payload.task_type, latest)
        snapshot = [
            ChecklistItem(
                task_id=task.id,
                item_code=tpl.item_code,
                item_name=tpl.item_name,
                checklist_version=latest,
                deprecated=False,
            )
            for tpl in template
        ]
        self.repo.add_checklist_items(snapshot)
        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="InspectionTask",
            event="InspectionTask.create",
            target_type="InspectionTask",
            target_id=task.id,
            task_id=task.id,
            building_id=task.building_id,
            checklist_version=latest,
        )
        self.db.commit()
        return task

    # ---------- 领取（巡检员，按楼栋） ----------
    def claim(self, task_id: int, actor: dict) -> InspectionTask:
        task = self.get(task_id)
        if task.status != PLANNED:
            if task.inspector_id and task.inspector_id != actor["id"]:
                raise ConflictError("TASK_ALREADY_CLAIMED", "该巡检任务已被其他巡检员领取")
            raise ConflictError("TASK_NOT_CLAIMABLE", "巡检任务当前状态不可领取")

        # 原子领取：仅当任务仍为 PLANNED 且无领取人时才能抢到。
        updated = (
            self.db.query(InspectionTask)
            .filter(
                InspectionTask.id == task_id,
                InspectionTask.status == PLANNED,
                InspectionTask.inspector_id.is_(None),
            )
            .update({InspectionTask.inspector_id: actor["id"], InspectionTask.status: IN_PROGRESS})
        )
        self.db.flush()
        if updated == 0:
            self.db.rollback()
            raise ConflictError("TASK_ALREADY_CLAIMED", "该巡检任务已被其他巡检员领取")
        task = self.get(task_id)
        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="InspectionTask",
            event="InspectionTask.claim",
            target_type="InspectionTask",
            target_id=task_id,
            inspector_id=actor["id"],
            task_id=task_id,
        )
        self.db.commit()
        return task

    # ---------- 复核（主管） ----------
    def review(self, task_id: int, approved: bool, actor: dict) -> InspectionTask:
        task = self.get(task_id)
        if task.status != SUBMITTED:
            raise ConflictError("TASK_NOT_CLAIMABLE", "只有待复验的巡检任务可以复核")
        task.status = REVIEWED if approved else SUBMITTED
        self.db.flush()
        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="InspectionTask",
            event="InspectionTask.review",
            target_type="InspectionTask",
            target_id=task_id,
            task_id=task_id,
            approved="通过" if approved else "退回",
        )
        self.db.commit()
        return task

    # ---------- 清单版本发布（主管） ----------
    def publish_checklist(self, payload, actor: dict) -> dict:
        if payload.task_type not in INITIAL_CHECKLISTS:
            raise ServiceError("VALIDATION_FAILED", "未知的巡检设备类型")
        if not payload.items:
            raise ServiceError("VALIDATION_FAILED", "新清单至少包含一个检查项")
        codes = [item.item_code for item in payload.items]
        if len(set(codes)) != len(codes):
            raise ServiceError("VALIDATION_FAILED", "清单内检查项编号重复")

        latest = self.repo.latest_template_version(payload.task_type)
        next_version = f"v{int((latest or 'v0').lstrip('v')) + 1}"
        tpl_rows = [
            ChecklistTemplate(
                task_type=payload.task_type,
                version=next_version,
                item_code=item.item_code,
                item_name=item.item_name,
            )
            for item in payload.items
        ]
        self.repo.add_template_items(tpl_rows)

        # 进行中（含已领取未提交）的任务：并入新项，旧集合中被删除的项标记过期。
        open_tasks = [
            row
            for row in self.repo.find_all()
            if row.task_type == payload.task_type and row.status not in CLOSED_TASK_STATUSES
        ]
        for task in open_tasks:
            old_items = self.repo.list_checklist_items(task.id)
            active_old = {item.item_code: item for item in old_items if not item.deprecated}
            removed = [code for code in active_old if code not in codes]
            self.repo.mark_deprecated(task.id, removed)
            existing_codes = {item.item_code for item in old_items}
            added = [
                ChecklistItem(
                    task_id=task.id,
                    item_code=item.item_code,
                    item_name=item.item_name,
                    checklist_version=next_version,
                    deprecated=False,
                )
                for item in payload.items
                if item.item_code not in existing_codes
            ]
            if added:
                self.repo.add_checklist_items(added)
            old_version = task.checklist_version
            task.checklist_version = next_version
            self.db.flush()
            write_audit_log(
                self.db,
                actor=actor["username"],
                entity="InspectionTask",
                event="InspectionTask.version",
                target_type="InspectionTask",
                target_id=task.id,
                task_id=task.id,
                old_version=old_version,
                new_version=next_version,
            )

        write_audit_log(
            self.db,
            actor=actor["username"],
            entity="Checklist",
            event="Checklist.publish",
            target_type="ChecklistTemplate",
            target_id=payload.task_type,
            task_type=payload.task_type,
            checklist_version=next_version,
        )
        self.db.commit()
        return {"task_type": payload.task_type, "checklist_version": next_version, "superseded_tasks": [t.id for t in open_tasks]}

    def seed_initial_templates(self):
        """首次启动时写入 v1 清单模板。"""
        for task_type, items in INITIAL_CHECKLISTS.items():
            if self.repo.latest_template_version(task_type):
                continue
            rows = [
                ChecklistTemplate(task_type=task_type, version="v1", item_code=code, item_name=name)
                for code, name in items
            ]
            self.repo.add_template_items(rows)
        self.db.commit()

    def snapshot_template_for_task(self, task: InspectionTask):
        """给种子数据中的任务补齐 v1 检查项快照。"""
        if self.repo.list_checklist_items(task.id):
            return
        template = self.repo.list_template(task.task_type, task.checklist_version) or []
        self.repo.add_checklist_items([
            ChecklistItem(
                task_id=task.id,
                item_code=tpl.item_code,
                item_name=tpl.item_name,
                checklist_version=task.checklist_version,
                deprecated=False,
            )
            for tpl in template
        ])

    def is_closed(self, task: InspectionTask) -> bool:
        return task.status in CLOSED_TASK_STATUSES
