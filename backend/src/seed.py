"""本地种子数据：启动时幂等写入（全部本地数据，禁止第三方 API）。

演示账号（用户名/密码相同）：
- inspector_a / inspector_b  巡检员
- maintainer_a               维保人员
- supervisor_a               物业主管
- auditor_a                  审计员
"""

import threading
from datetime import timedelta

from sqlalchemy import select

from src.constants.device_type import DEVICE_CHECKLIST
from src.database.session import SessionLocal, init_db
from src.models.entities import (
    Building,
    FireDevice,
    HazardTicket,
    InspectionResult,
    InspectionTask,
    TaskChecklistItem,
    User,
    utcnow,
)

_SEED_LOCK = threading.Lock()

USERS = [
    ("inspector_a", "巡检员-安小检", "INSPECTOR"),
    ("inspector_b", "巡检员-安小巡", "INSPECTOR"),
    ("maintainer_a", "维保-老周", "MAINTAINER"),
    ("supervisor_a", "主管-陈主任", "SUPERVISOR"),
    ("auditor_a", "审计-林审计", "AUDITOR"),
]

BUILDINGS = [
    ("1号研发楼", "云溪科技园", 8, "一级", "310100-A01"),
    ("2号综合楼", "云溪科技园", 5, "二级", "310100-A02"),
    ("3号仓储楼", "云溪科技园", 3, "二级", "310100-A03"),
]

# (楼栋下标, 编码, 类型, 楼层, 位置, 状态, 距下次维保天数)
DEVICES = [
    (0, "HYD-101", "HYDRANT", "1F", "东侧楼梯口", "NORMAL", 30),
    (0, "EXT-102", "EXTINGUISHER", "2F", "走廊西端", "NORMAL", 12),
    (0, "SMK-103", "SMOKE_DETECTOR", "3F", "开放办公区", "NORMAL", 60),
    (0, "SPK-104", "SPRINKLER", "4F", "会议室吊顶", "NORMAL", 45),
    (0, "EXL-105", "EXIT_LIGHT", "1F", "安全出口上方", "NORMAL", 20),
    (1, "HYD-201", "HYDRANT", "1F", "大堂北侧", "NORMAL", 15),
    (1, "EXT-202", "EXTINGUISHER", "3F", "茶水间门口", "FAULT", 5),
    (2, "SMK-301", "SMOKE_DETECTOR", "1F", "入库区", "MAINTAINING", 90),
]


def seed_database() -> None:
    init_db()
    # 进程内锁：多个 TestClient/worker 并发启动时只允许一个执行种子写入
    with _SEED_LOCK:
        session = SessionLocal()
        try:
            if session.scalars(select(User)).first() is not None:
                return  # 已初始化，保持幂等
            _seed_users_and_demo_data(session)
        finally:
            session.close()


def _seed_users_and_demo_data(session) -> None:
    now = utcnow()
    users: dict[str, User] = {}
    for username, name, role in USERS:
        user = User(username=username, password=username, name=name, role=role)
        session.add(user)
        users[username] = user
    session.flush()

    buildings: list[Building] = []
    for index, (name, campus, floors, grade, code) in enumerate(BUILDINGS):
        manager = users["supervisor_a"] if index == 0 else None
        building = Building(
            name=name,
            campus=campus,
            floor_count=floors,
            fire_grade=grade,
            address_code=code,
            manager_id=manager.id if manager else None,
        )
        session.add(building)
        buildings.append(building)
    session.flush()

    devices: list[FireDevice] = []
    for b_idx, code, dtype, floor, loc, status, next_days in DEVICES:
        device = FireDevice(
            building_id=buildings[b_idx].id,
            device_code=code,
            device_type=dtype,
            floor=floor,
            location_desc=loc,
            install_date=now - timedelta(days=400),
            status=status,
            next_maintenance_at=now + timedelta(days=next_days),
        )
        session.add(device)
        devices.append(device)
    session.flush()

    # 任务1：1号楼消火栓，巡检员A 已领取、巡检中
    task1 = InspectionTask(
        building_id=buildings[0].id,
        inspector_id=users["inspector_a"].id,
        plan_date=now - timedelta(days=1),
        task_type="HYDRANT",
        status="IN_PROGRESS",
        checklist_version=1,
    )
    # 任务2：1号楼灭火器，待领取
    task2 = InspectionTask(
        building_id=buildings[0].id,
        plan_date=now + timedelta(days=1),
        task_type="EXTINGUISHER",
        status="PLANNED",
        checklist_version=1,
    )
    # 任务3：2号楼消火栓，已提交待复验（含一个异常隐患：已派单整改完成待复验）
    task3 = InspectionTask(
        building_id=buildings[1].id,
        inspector_id=users["inspector_b"].id,
        plan_date=now - timedelta(days=5),
        task_type="HYDRANT",
        status="SUBMITTED",
        checklist_version=1,
        finished_at=now - timedelta(days=4),
    )
    # 任务4：3号楼烟感，已复验关闭（留一条已关闭隐患的历史）
    task4 = InspectionTask(
        building_id=buildings[2].id,
        inspector_id=users["inspector_a"].id,
        plan_date=now - timedelta(days=20),
        task_type="SMOKE_DETECTOR",
        status="REVIEWED",
        checklist_version=1,
        finished_at=now - timedelta(days=19),
        reviewed_at=now - timedelta(days=18),
    )
    session.add_all([task1, task2, task3, task4])
    session.flush()

    hyd1 = devices[0]
    hyd201 = devices[5]
    smk301 = devices[7]

    def add_items(task: InspectionTask, device: FireDevice) -> list[TaskChecklistItem]:
        rows = []
        for code, name in DEVICE_CHECKLIST[task.task_type]:
            row = TaskChecklistItem(
                task_id=task.id,
                device_id=device.id,
                item_code=f"{device.id}-{code}",
                item_name=name,
                checklist_version=1,
            )
            session.add(row)
            rows.append(row)
        return rows

    items1 = add_items(task1, hyd1)
    add_items(task2, devices[1])  # 1号楼灭火器
    items3 = add_items(task3, hyd201)
    items4 = add_items(task4, smk301)
    session.flush()

    # 任务1：已完成 1/3（第一项正常）
    session.add(
        InspectionResult(
            task_id=task1.id, device_id=hyd1.id, item_code=items1[0].item_code,
            result_status="NORMAL", measured_value="0.6MPa", note="压力正常",
            submitted_by=users["inspector_a"].id, submitted_at=now - timedelta(hours=2),
        )
    )

    # 任务3：3 项全部提交，阀门异常 -> 隐患单待复验
    r3a = InspectionResult(
        task_id=task3.id, device_id=hyd201.id, item_code=items3[0].item_code,
        result_status="NORMAL", measured_value="0.55MPa", note="压力正常",
        submitted_by=users["inspector_b"].id, submitted_at=now - timedelta(days=4),
    )
    r3b = InspectionResult(
        task_id=task3.id, device_id=hyd201.id, item_code=items3[1].item_code,
        result_status="ABNORMAL", measured_value="无法启闭", note="阀门锈蚀卡死",
        submitted_by=users["inspector_b"].id, submitted_at=now - timedelta(days=4),
    )
    r3c = InspectionResult(
        task_id=task3.id, device_id=hyd201.id, item_code=items3[2].item_code,
        result_status="NORMAL", measured_value="齐全", note="水带枪头完好",
        submitted_by=users["inspector_b"].id, submitted_at=now - timedelta(days=4),
    )
    session.add_all([r3a, r3b, r3c])
    session.flush()
    session.add(
        HazardTicket(
            result=r3b, severity="HIGH", owner_id=users["maintainer_a"].id,
            deadline=now - timedelta(days=1), rectify_status="RECTIFIED",
            rectify_note="已更换阀门并做防锈处理", created_at=now - timedelta(days=4),
            rectified_at=now - timedelta(days=2),
        )
    )

    # 任务4：烟感测试异常 -> 已整改复验关闭
    r4 = InspectionResult(
        task_id=task4.id, device_id=smk301.id, item_code=items4[1].item_code,
        result_status="ABNORMAL", measured_value="无响应", note="测试键不报警",
        submitted_by=users["inspector_a"].id, submitted_at=now - timedelta(days=19),
    )
    session.add(r4)
    session.flush()
    session.add(
        HazardTicket(
            result=r4, severity="MEDIUM", owner_id=users["maintainer_a"].id,
            deadline=now - timedelta(days=15), rectify_status="CLOSED",
            rectify_note="更换探测器主板", created_at=now - timedelta(days=19),
            rectified_at=now - timedelta(days=17), closed_at=now - timedelta(days=18),
            closed_by=users["supervisor_a"].id,
        )
    )
    session.commit()
