"""端到端流程验证：领取 -> 逐项提交 -> 异常生单 -> 整改 -> 复验关闭 -> 状态/总览重算。"""

import os
import sys

os.environ["SQLITE_URL"] = "sqlite:///./test_e2e.db"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402

failures = []


def check(name: str, condition: bool, detail=""):
    print(("PASS" if condition else "FAIL"), "-", name, detail)
    if not condition:
        failures.append(name)


with TestClient(app) as client:
    def login(username: str) -> dict:
        res = client.post("/api/auth/login", json={"username": username, "password": username})
        assert res.status_code == 200, res.text
        body = res.json()
        return {"Authorization": f"Bearer {body['access_token']}"}

    inspector_a = login("inspector_a")
    inspector_b = login("inspector_b")
    maintainer = login("maintainer_a")
    supervisor = login("supervisor_a")
    auditor = login("auditor_a")

    # ---------- 0. 基础鉴权 ----------
    check("未登录访问被拒绝", client.get("/api/building").status_code == 401)
    check(
        "巡检员不能排期(403)",
        client.post(
            "/api/inspection-task",
            headers=inspector_a,
            json={"building_id": 1, "task_type": "HYDRANT"},
        ).status_code
        == 403,
    )
    check(
        "维保人员不能领取任务(403)",
        client.post("/api/inspection-task/2/claim", headers=maintainer).status_code == 403,
    )
    check(
        "审计员不能整改隐患(403)",
        client.post(
            "/api/hazard-ticket/1/rectify", headers=auditor, json={"rectify_note": "x"}
        ).status_code
        == 403,
    )

    # ---------- 1. 主管按楼栋排期，生成清单 ----------
    created = client.post(
        "/api/inspection-task",
        headers=supervisor,
        json={"building_id": 2, "task_type": "EXTINGUISHER"},
    )
    check("主管排期成功", created.status_code == 200, created.text)
    new_task = created.json()
    new_task_id = new_task["id"]
    check("排期生成 1 台设备*3 项清单", new_task["total_items"] == 3, str(new_task["total_items"]))
    check("初始状态待领取", new_task["status"] == "PLANNED")
    check("清单版本从 v1 开始", new_task["checklist_version"] == 1)

    # ---------- 2. 巡检员领取，并发只允许一人成功 ----------
    r1 = client.post(f"/api/inspection-task/{new_task_id}/claim", headers=inspector_a)
    r2 = client.post(f"/api/inspection-task/{new_task_id}/claim", headers=inspector_b)
    check("巡检员A领取成功", r1.status_code == 200, r1.text)
    check("巡检员B重复领取被拒绝", r2.status_code == 409, r2.text)
    check("重复领取错误码 TASK_NOT_CLAIMABLE", r2.json()["code"] == "TASK_NOT_CLAIMABLE")

    # ---------- 3. 逐项提交，异常生成隐患单 ----------
    items = r1.json()["items"]
    normal_item = items[0]
    abnormal_item = items[1]
    third_item = items[2]

    def submit(headers, body):
        return client.post(
            f"/api/inspection-result/task/{new_task_id}/submit", headers=headers, json=body
        )

    # 巡检员B（未领取该任务）不能提交
    forbidden = submit(inspector_b, {"items": [{
        "item_code": normal_item["item_code"], "checklist_version": 1,
        "result_status": "NORMAL", "note": "b tries",
    }]})
    check("非领取人提交被拒绝", forbidden.status_code == 403, forbidden.text)

    # A 提交第一项正常
    ok1 = submit(inspector_a, {"items": [{
        "item_code": normal_item["item_code"], "checklist_version": 1,
        "result_status": "NORMAL", "measured_value": "压力正常",
    }]})
    check("正常项提交成功", ok1.status_code == 200, ok1.text)
    check("正常项不生成隐患单", ok1.json()["saved"][0]["hazard_id"] is None)

    # 同一项的唯一约束兜底：直接用数据库层验证（两名巡检员不能落两份结果）
    from src.database.session import SessionLocal  # noqa: E402
    from src.models.entities import InspectionResult  # noqa: E402
    from sqlalchemy import func, select  # noqa: E402

    with SessionLocal() as session:
        count = session.scalar(
            select(func.count(InspectionResult.id)).where(
                InspectionResult.task_id == new_task_id,
                InspectionResult.item_code == normal_item["item_code"],
            )
        )
    check("同一检查项只落一份结果", count == 1, str(count))

    # A 提交第二项异常
    ab = submit(inspector_a, {"items": [{
        "item_code": abnormal_item["item_code"], "checklist_version": 1,
        "result_status": "ABNORMAL", "severity": "HIGH",
        "measured_value": "压力不足", "note": "压力表红区",
    }]})
    check("异常项提交成功", ab.status_code == 200, ab.text)
    hazard_id = ab.json()["saved"][0]["hazard_id"]
    check("异常项自动生成隐患单", hazard_id is not None)

    # 设备状态立即重算为 MAINTAINING
    devices = client.get("/api/fire-device?building_id=2", headers=inspector_a).json()
    abn_device = next(d for d in devices if d["id"] == abnormal_item["device_id"])
    check("隐患生成后设备状态为整改中", abn_device["status"] == "MAINTAINING", abn_device["status"])

    # 第三项正常
    ok3 = submit(inspector_a, {"items": [{
        "item_code": third_item["item_code"], "checklist_version": 1,
        "result_status": "NORMAL", "note": "在有效期内",
    }]})
    check("第三项提交成功", ok3.status_code == 200)

    # ---------- 4. 版本冲突：主管升级清单，旧版本拒绝、新版本照收 ----------
    bumped = client.post(
        f"/api/inspection-task/{new_task_id}/checklist-version", headers=supervisor
    )
    check("主管升级清单版本", bumped.status_code == 200)
    check("当前清单版本变为 v2", bumped.json()["checklist_version"] == 2)

    stale = submit(inspector_a, {"items": [{
        "item_code": normal_item["item_code"], "checklist_version": 1,
        "result_status": "NORMAL", "note": "旧版本补提交",
    }]})
    check("旧版本提交不整体报错(200)", stale.status_code == 200, stale.text)
    conflict = stale.json()["conflicts"][0]
    check("旧项冲突码为版本冲突", conflict["code"] == "CHECKLIST_VERSION_CONFLICT", str(conflict))
    check("冲突说明包含当前版本 v2", "v2" in conflict["message"], conflict["message"])
    check("旧项没有落库结果", len(stale.json()["saved"]) == 0)

    fresh = submit(inspector_a, {"items": [{
        "item_code": normal_item["item_code"], "checklist_version": 2,
        "result_status": "NORMAL", "measured_value": "0.58MPa", "note": "新版本复测",
    }]})
    check("新版本项照常保存", fresh.status_code == 200 and len(fresh.json()["saved"]) == 1, fresh.text)

    # 混合批次：一项过期 + 一项有效（异常->已有隐患单复用）
    mixed = submit(inspector_a, {"items": [
        {"item_code": third_item["item_code"], "checklist_version": 1,
         "result_status": "NORMAL", "note": "旧"},
        {"item_code": abnormal_item["item_code"], "checklist_version": 2,
         "result_status": "ABNORMAL", "severity": "CRITICAL", "note": "仍异常"},
    ]})
    check("混合批次 200 返回", mixed.status_code == 200)
    check("混合批次 1 项冲突 1 项保存",
          len(mixed.json()["conflicts"]) == 1 and len(mixed.json()["saved"]) == 1, mixed.text)
    hazards = client.get("/api/hazard-ticket", headers=supervisor).json()
    same_item_hazards = [h for h in hazards if h["item_code"] == abnormal_item["item_code"]
                         and h["task_id"] == new_task_id]
    check("同一异常结果只保留一张隐患单", len(same_item_hazards) == 1, str(len(same_item_hazards)))

    # ---------- 5. 提交复核 -> 主管复验关闭任务 ----------
    submit_review = client.post(
        f"/api/inspection-task/{new_task_id}/submit", headers=inspector_a
    )
    check("全部完成后提交复核", submit_review.status_code == 200, submit_review.text)
    check("任务状态待复验", submit_review.json()["status"] == "SUBMITTED")

    reviewed = client.post(
        f"/api/inspection-task/{new_task_id}/review", headers=supervisor, json={"note": "合格"}
    )
    check("主管复验关闭任务", reviewed.status_code == 200)
    check("任务状态已复验关闭", reviewed.json()["status"] == "REVIEWED")
    check("复验后不允许再提交项", submit(inspector_a, {"items": [{
        "item_code": normal_item["item_code"], "checklist_version": 2,
        "result_status": "NORMAL",
    }]}).status_code == 409)

    # ---------- 6. 隐患派单 -> 整改 -> 复验关闭，设备恢复 ----------
    ticket = same_item_hazards[0]
    tid = ticket["id"]
    check("隐患单初始待派单", ticket["rectify_status"] == "OPEN", ticket["rectify_status"])

    assign = client.post(
        f"/api/hazard-ticket/{tid}/assign",
        headers=supervisor,
        json={"owner_id": 3, "severity": "HIGH"},
    )
    check("主管派单维保", assign.status_code == 200, assign.text)
    check("派单后待整改", assign.json()["rectify_status"] == "ASSIGNED")

    bad_rectify = client.post(
        f"/api/hazard-ticket/{tid}/rectify",
        headers=inspector_a,
        json={"rectify_note": "越权"},
    )
    check("巡检员不能整改", bad_rectify.status_code == 403)

    rectify = client.post(
        f"/api/hazard-ticket/{tid}/rectify",
        headers=maintainer,
        json={"rectify_note": "更换压力表并充装"},
    )
    check("维保提交整改", rectify.status_code == 200, rectify.text)
    check("整改后待复验", rectify.json()["rectify_status"] == "RECTIFIED")

    # 复验不通过退回
    reject = client.post(
        f"/api/hazard-ticket/{tid}/close",
        headers=supervisor,
        json={"note": "仍有渗漏", "pass_review": False},
    )
    check("复验不通过退回整改", reject.status_code == 200)
    check("退回后状态为待整改", reject.json()["rectify_status"] == "ASSIGNED")
    devices = client.get("/api/fire-device?building_id=2", headers=supervisor).json()
    check("退回后设备仍是整改中",
          next(d for d in devices if d["id"] == abnormal_item["device_id"])["status"] == "MAINTAINING")

    client.post(
        f"/api/hazard-ticket/{tid}/rectify",
        headers=maintainer,
        json={"rectify_note": "重新紧固密封"},
    )
    close = client.post(
        f"/api/hazard-ticket/{tid}/close",
        headers=supervisor,
        json={"note": "复验合格", "pass_review": True},
    )
    check("复验通过关闭隐患", close.status_code == 200, close.text)
    check("隐患状态已关闭", close.json()["rectify_status"] == "CLOSED")
    devices = client.get("/api/fire-device?building_id=2", headers=supervisor).json()
    check("隐患关闭后设备恢复正常",
          next(d for d in devices if d["id"] == abnormal_item["device_id"])["status"] == "NORMAL")

    # ---------- 7. 总览/报表重算 ----------
    dash = client.get("/api/stats/dashboard", headers=supervisor).json()
    check("总览设备总数=8", dash["device_total"] == 8, str(dash))
    check("完成率是数值", 0 <= dash["inspection_completion_rate"] <= 1)
    check("整改率是数值", 0 <= dash["rectification_rate"] <= 1)
    report = client.get("/api/stats/monthly-report", headers=auditor).json()
    check("月度报表非空", len(report) >= 1)

    # ---------- 8. 审计日志 ----------
    logs = client.get("/api/auth/audit-logs", headers=auditor)
    check("审计员可查看日志", logs.status_code == 200)
    actions = {row["action"] for row in logs.json()}
    for required in (
        "InspectionTask.create", "InspectionTask.claim",
        "InspectionResult.batch_submit", "HazardTicket.assign",
        "HazardTicket.rectify", "HazardTicket.close",
    ):
        check(f"审计日志含 {required}", required in actions, str(sorted(actions)))
    check("巡检员不能查看审计日志",
          client.get("/api/auth/audit-logs", headers=inspector_a).status_code == 403)

print()
if failures:
    print(f"{len(failures)} 项失败：", failures)
    sys.exit(1)
print("全部通过")
