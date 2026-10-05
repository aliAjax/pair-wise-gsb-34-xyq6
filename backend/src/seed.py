"""首次启动时播种演示数据：4 个角色账号、2 栋楼、若干设备、待领取巡检任务。"""
from datetime import date

from sqlalchemy.orm import Session

from src.constants.inspection_status import PLANNED
from src.constants.roles import (
    ROLE_AUDITOR,
    ROLE_INSPECTOR,
    ROLE_MAINTAINER,
    ROLE_SUPERVISOR,
)
from src.models.building import Building
from src.models.fire_device import FireDevice
from src.models.inspection_task import InspectionTask
from src.models.user import User
from src.services.inspection_task_service import InspectionTaskService
from src.utils.security import hash_password

# 演示账号（用户名/密码一致），前端登录页直接展示。
DEMO_USERS = [
    ("inspector", "李巡", ROLE_INSPECTOR),
    ("inspector2", "王检", ROLE_INSPECTOR),
    ("maintainer", "赵维保", ROLE_MAINTAINER),
    ("supervisor", "周主管", ROLE_SUPERVISOR),
    ("auditor", "钱审计", ROLE_AUDITOR),
]


def seed_database(db: Session):
    if db.query(User).count() > 0:
        return

    for username, display_name, role in DEMO_USERS:
        db.add(User(username=username, display_name=display_name, role=role,
                    password_hash=hash_password(username)))

    b1 = Building(name="云谷科技园 A 栋", campus="云谷科技园", floor_count=12,
                  fire_grade="一级", manager_id=4, address_code="330106-A")
    b2 = Building(name="云谷科技园 B 栋", campus="云谷科技园", floor_count=8,
                  fire_grade="二级", manager_id=4, address_code="330106-B")
    db.add_all([b1, b2])
    db.flush()

    devices = [
        FireDevice(building_id=b1.id, device_code="MHQ-A-0101", device_type="EXTINGUISHER",
                   floor="1", location_desc="大堂东侧", install_date=date.fromisoformat("2024-03-01"),
                   status="NORMAL", next_maintenance_at=date.fromisoformat("2026-12-01")),
        FireDevice(building_id=b1.id, device_code="XHS-A-0201", device_type="HYDRANT",
                   floor="2", location_desc="电梯厅西侧", install_date=date.fromisoformat("2023-06-15"),
                   status="NORMAL", next_maintenance_at=date.fromisoformat("2026-11-15")),
        FireDevice(building_id=b1.id, device_code="YG-A-0501", device_type="SMOKE_DETECTOR",
                   floor="5", location_desc="走廊吊顶", install_date=date.fromisoformat("2023-09-01"),
                   status="NORMAL", next_maintenance_at=date.fromisoformat("2026-10-01")),
        FireDevice(building_id=b1.id, device_code="PL-A-0801", device_type="SPRINKLER",
                   floor="8", location_desc="机房上方", install_date=date.fromisoformat("2023-09-01"),
                   status="NORMAL", next_maintenance_at=date.fromisoformat("2026-10-01")),
        FireDevice(building_id=b2.id, device_code="SS-B-0101", device_type="EXIT_LIGHT",
                   floor="1", location_desc="安全出口上方", install_date=date.fromisoformat("2024-01-10"),
                   status="NORMAL", next_maintenance_at=date.fromisoformat("2026-12-10")),
        FireDevice(building_id=b2.id, device_code="MHQ-B-0301", device_type="EXTINGUISHER",
                   floor="3", location_desc="楼梯口", install_date=date.fromisoformat("2024-01-10"),
                   status="NORMAL", next_maintenance_at=date.fromisoformat("2026-12-10")),
    ]
    db.add_all(devices)
    db.flush()

    task_service = InspectionTaskService(db)
    task_service.seed_initial_templates()

    t1 = InspectionTask(building_id=b1.id, inspector_id=None, plan_date="2026-10-05",
                        task_type="EXTINGUISHER", status=PLANNED, checklist_version="v1")
    t2 = InspectionTask(building_id=b1.id, inspector_id=None, plan_date="2026-10-05",
                        task_type="HYDRANT", status=PLANNED, checklist_version="v1")
    t3 = InspectionTask(building_id=b2.id, inspector_id=None, plan_date="2026-10-06",
                        task_type="EXIT_LIGHT", status=PLANNED, checklist_version="v1")
    db.add_all([t1, t2, t3])
    db.flush()
    for task in (t1, t2, t3):
        task_service.snapshot_template_for_task(task)

    db.commit()
