"""角色权限矩阵：巡检员/维保人员/主管/审计员只能执行各自的动作。"""


def test_auth_required_without_token(client):
    assert client.get("/api/building").status_code == 401
    assert client.get("/api/dashboard/overview").status_code == 401


def test_invalid_token_rejected(client):
    resp = client.get("/api/building", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401
    assert resp.json()["code"] == "TOKEN_INVALID"


def test_inspector_permissions(client, auth):
    hi = auth("inspector")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    # 巡检员不能派单/复验隐患
    assert client.post(f"/api/hazard-ticket/1/assign", headers=hi, json={"owner_id": 3}).status_code == 403
    # 不能发布清单
    assert client.post("/api/inspection-task/checklist/publish", headers=hi,
                       json={"task_type": "HYDRANT", "items": []}).status_code == 403
    # 不能看审计日志
    assert client.get("/api/audit-log", headers=hi).status_code == 403
    # 可以领取任务、读清单
    assert client.post(f"/api/inspection-task/{task_id}/claim", headers=hi).status_code == 200
    assert client.get(f"/api/inspection-task/{task_id}/checklist", headers=hi).status_code == 200


def test_maintainer_permissions(client, auth):
    hm = auth("maintainer")
    hi = auth("inspector")
    # 不能领取任务
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    assert client.post(f"/api/inspection-task/{task_id}/claim", headers=hm).status_code == 403
    # 不能派单/复验
    assert client.post("/api/hazard-ticket/1/assign", headers=hm, json={"owner_id": 3}).status_code == 403
    assert client.post("/api/hazard-ticket/1/review", headers=hm, json={"approved": True}).status_code == 403
    assert client.get("/api/audit-log", headers=hm).status_code == 403


def test_supervisor_permissions(client, auth):
    hs = auth("supervisor")
    # 主管不能领取巡检任务
    task_id = client.get("/api/inspection-task", headers=hs).json()[0]["id"]
    assert client.post(f"/api/inspection-task/{task_id}/claim", headers=hs).status_code == 403
    # 主管不能代替维保提交整改
    assert client.post("/api/hazard-ticket/1/rectify", headers=hs,
                       json={"rectify_note": "x"}).status_code == 403
    # 可以排期任务、看审计日志
    assert client.post("/api/inspection-task", headers=hs,
                       json={"building_id": 1, "plan_date": "2026-10-10", "task_type": "HYDRANT"}).status_code == 200
    assert client.get("/api/audit-log", headers=hs).status_code == 200


def test_auditor_read_only(client, auth):
    ha = auth("auditor")
    task_id = 1
    assert client.post(f"/api/inspection-task/{task_id}/claim", headers=ha).status_code == 403
    assert client.post("/api/hazard-ticket/1/assign", headers=ha, json={"owner_id": 3}).status_code == 403
    # 只读接口与审计日志可访问
    assert client.get("/api/audit-log", headers=ha).status_code == 200
    assert client.get("/api/dashboard/overview", headers=ha).status_code == 200
    assert client.get("/api/fire-device", headers=ha).status_code == 200


def test_owner_only_rectification(client, auth):
    # 只有被派单的维保人员本人能提交整改
    hi, hm, hs = auth("inspector"), auth("maintainer"), auth("supervisor")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)
    chk = client.get(f"/api/inspection-task/{task_id}/checklist", headers=hi).json()
    device_id = client.get(f"/api/fire-device?building_id={chk['task']['building_id']}", headers=hi).json()[0]["id"]
    items = [{"device_id": device_id, "item_code": i["item_code"], "result_status": "ABNORMAL"} for i in chk["items"]]
    client.post(f"/api/inspection-result/task/{task_id}/submit", headers=hi,
                json={"checklist_version": chk["current_version"], "items": items})
    ticket_id = client.get("/api/hazard-ticket", headers=hs).json()[0]["id"]
    # 未派单不能整改
    assert client.post(f"/api/hazard-ticket/{ticket_id}/rectify", headers=hm,
                       json={"rectify_note": "x"}).status_code == 409
    client.post(f"/api/hazard-ticket/{ticket_id}/assign", headers=hs, json={"owner_id": 3})
    assert client.post(f"/api/hazard-ticket/{ticket_id}/rectify", headers=hm,
                       json={"rectify_note": "本人整改"}).status_code == 200


def test_audit_logs_record_write_actions(client, auth):
    hi, hs = auth("inspector"), auth("supervisor")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)
    logs = client.get("/api/audit-log?limit=50", headers=hs).json()
    actions = {log["action"] for log in logs}
    assert "InspectionTask.claim" in actions
