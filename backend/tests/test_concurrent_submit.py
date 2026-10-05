"""并发专项：两名不同巡检员双会话同时领取/提交同一任务，
最终只能落一份结果和一张隐患单。"""

import os
import sys
import threading

os.environ["SQLITE_URL"] = "sqlite:///./test_concurrent.db"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402
from src.database.session import SessionLocal, init_db  # noqa: E402
from src.seed import seed_database  # noqa: E402
from src.models.entities import HazardTicket, InspectionResult, InspectionTask  # noqa: E402
from sqlalchemy import func, select  # noqa: E402

# 生产环境只有单个后端进程在启动时初始化；测试也先初始化一次，
# 避免两个 TestClient 并发启动时同时对一个刚删除的库建表
seed_database()


def _claim(client: TestClient, headers: dict, task_id: int, outcome: dict):
    res = client.post(f"/api/inspection-task/{task_id}/claim", headers=headers)
    outcome["claim_status"] = res.status_code


def _submit(client: TestClient, headers: dict, task_id: int, item_code: str, who: str, outcome: dict):
    res = client.post(
        f"/api/inspection-result/task/{task_id}/submit",
        headers=headers,
        json={"items": [{
            "item_code": item_code,
            "checklist_version": 1,
            "result_status": "ABNORMAL",
            "severity": "HIGH",
            "note": who,
        }]},
    )
    outcome["status"] = res.status_code
    outcome["body"] = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}


with TestClient(app) as c1, TestClient(app) as c2:
    def token(client, username):
        return {"Authorization": f"Bearer {client.post('/api/auth/login', json={'username': username, 'password': username}).json()['access_token']}"}

    sup = token(c1, "supervisor_a")
    insp_a = token(c1, "inspector_a")
    insp_b = token(c2, "inspector_b")

    # 主管建任务：1号楼 EXTINGUISHER 一台设备
    task = c1.post(
        "/api/inspection-task",
        headers=sup,
        json={"building_id": 1, "task_type": "EXTINGUISHER"},
    ).json()
    task_id = task["id"]
    item_code = task["items"][0]["item_code"]

    # 1) 并发领取：条件更新保证只有一人成功
    oa, ob = {}, {}
    t1 = threading.Thread(target=_claim, args=(c1, insp_a, task_id, oa))
    t2 = threading.Thread(target=_claim, args=(c2, insp_b, task_id, ob))
    t1.start(); t2.start(); t1.join(); t2.join()
    assert sorted([oa["claim_status"], ob["claim_status"]]) == [200, 409], (oa, ob)
    print("并发领取：一人成功一人 409 ✓")

    # 落库确认 inspector_id 只被设置一次且未被覆盖
    with SessionLocal() as session:
        claimed_by = session.get(InspectionTask, task_id).inspector_id
    assert claimed_by in (1, 2)

    # 2) 未领取者直接提交必须被 RBAC/归属拒绝
    loser = insp_b if oa["claim_status"] == 200 else insp_a
    winner = insp_a if oa["claim_status"] == 200 else insp_b
    blocked = c2 if loser is insp_b else c1
    denied = blocked.post(
        f"/api/inspection-result/task/{task_id}/submit",
        headers=loser,
        json={"items": [{"item_code": item_code, "checklist_version": 1, "result_status": "ABNORMAL"}]},
    )
    assert denied.status_code == 403, denied.text
    print("未领取巡检员提交被拒绝 ✓")

    # 3) 领取者两个线程同时提交同一检查项（双端双击），唯一约束兜底
    winner_client = c1 if winner is insp_a else c2
    s1, s2 = {}, {}
    t1 = threading.Thread(target=_submit, args=(winner_client, winner, task_id, item_code, "tab-1", s1))
    t2 = threading.Thread(target=_submit, args=(winner_client, winner, task_id, item_code, "tab-2", s2))
    t1.start(); t2.start(); t1.join(); t2.join()
    print("submit1:", s1.get("status"), s1.get("body", {}).get("saved"), s1.get("body", {}).get("conflicts"))
    print("submit2:", s2.get("status"), s2.get("body", {}).get("saved"), s2.get("body", {}).get("conflicts"))
    assert s1["status"] == 200 and s2["status"] == 200

    with SessionLocal() as session:
        result_count = session.scalar(
            select(func.count(InspectionResult.id)).where(
                InspectionResult.task_id == task_id,
                InspectionResult.item_code == item_code,
            )
        )
        hazard_count = session.scalar(
            select(func.count(HazardTicket.id))
            .join(InspectionResult, HazardTicket.result_id == InspectionResult.id)
            .where(InspectionResult.task_id == task_id, InspectionResult.item_code == item_code)
        )
    assert result_count == 1, f"期望 1 份结果，实际 {result_count}"
    assert hazard_count == 1, f"期望 1 张隐患单，实际 {hazard_count}"
    print("并发提交：仅落一份结果和一张隐患单 ✓")
