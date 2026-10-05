"""并发与冲突：双巡检员领取/提交互斥、清单版本过期拒绝旧项、未过期项照常保存。"""


def test_claim_is_first_come_first_served(client, auth):
    hi, hi2 = auth("inspector"), auth("inspector2")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    r1 = client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)
    r2 = client.post(f"/api/inspection-task/{task_id}/claim", headers=hi2)
    assert r1.status_code == 200
    assert r2.status_code == 409
    assert r2.json()["code"] == "TASK_ALREADY_CLAIMED"
    task = [t for t in client.get("/api/inspection-task", headers=hi).json() if t["id"] == task_id][0]
    assert task["inspector_id"] == 1


def test_non_owner_cannot_submit(client, auth):
    hi, hi2 = auth("inspector"), auth("inspector2")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)
    chk = client.get(f"/api/inspection-task/{task_id}/checklist", headers=hi).json()
    device_id = client.get(f"/api/fire-device?building_id={chk['task']['building_id']}", headers=hi).json()[0]["id"]
    item = chk["items"][0]
    resp = client.post(
        f"/api/inspection-result/task/{task_id}/submit",
        headers=hi2,
        json={"checklist_version": chk["current_version"],
              "items": [{"device_id": device_id, "item_code": item["item_code"], "result_status": "NORMAL"}]},
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "TASK_NOT_OWNED"


def test_duplicate_submit_after_completion_rejected(client, auth):
    hi = auth("inspector")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)
    chk = client.get(f"/api/inspection-task/{task_id}/checklist", headers=hi).json()
    device_id = client.get(f"/api/fire-device?building_id={chk['task']['building_id']}", headers=hi).json()[0]["id"]
    items = [{"device_id": device_id, "item_code": i["item_code"], "result_status": "NORMAL"} for i in chk["items"]]
    payload = {"checklist_version": chk["current_version"], "items": items}
    first = client.post(f"/api/inspection-result/task/{task_id}/submit", headers=hi, json=payload)
    assert first.json()["task_status"] == "SUBMITTED"
    second = client.post(f"/api/inspection-result/task/{task_id}/submit", headers=hi, json=payload)
    assert second.status_code == 409
    assert second.json()["code"] == "TASK_CLOSED"
    # 结果仍只有一份/项，隐患单不重复
    results = client.get(f"/api/inspection-result?task_id={task_id}", headers=hi).json()
    assert len(results) == len(items)
    assert len({r["item_code"] for r in results}) == len(items)


def test_stale_checklist_rejects_old_items_keeps_current(client, auth):
    hi, hs = auth("inspector"), auth("supervisor")
    # 领取一个消火栓任务（v1 含 HYD_WATER/HYD_BOX/HYD_SEAL）
    tasks = client.get("/api/inspection-task?status=PLANNED", headers=hi).json()
    hydrant = [t for t in tasks if t["task_type"] == "HYDRANT"][0]
    task_id = hydrant["id"]
    client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)

    # 主管发布 v2：删除 HYD_BOX、HYD_SEAL，新增 HYD_NEW
    publish = client.post("/api/inspection-task/checklist/publish", headers=hs, json={
        "task_type": "HYDRANT",
        "items": [
            {"item_code": "HYD_WATER", "item_name": "水压正常"},
            {"item_code": "HYD_NEW", "item_name": "新增项"},
        ],
    })
    assert publish.status_code == 200
    assert publish.json()["checklist_version"] == "v2"

    chk = client.get(f"/api/inspection-task/{task_id}/checklist", headers=hi).json()
    assert chk["current_version"] == "v2"
    device_id = client.get(f"/api/fire-device?building_id={chk['task']['building_id']}", headers=hi).json()[0]["id"]

    # 巡检员仍持 v1：旧项 HYD_SEAL 拒绝；未过期项 HYD_WATER 照常保存；新项 HYD_NEW 提示补检
    resp = client.post(
        f"/api/inspection-result/task/{task_id}/submit",
        headers=hi,
        json={
            "checklist_version": "v1",
            "items": [
                {"device_id": device_id, "item_code": "HYD_WATER", "result_status": "NORMAL"},
                {"device_id": device_id, "item_code": "HYD_SEAL", "result_status": "NORMAL"},
            ],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["stale"] is True
    saved = {row["item_code"] for row in body["saved"]}
    rejected = {row["item_code"]: row["reason_code"] for row in body["rejected"]}
    assert saved == {"HYD_WATER"}
    assert rejected["HYD_SEAL"] == "CHECKLIST_STALE"
    assert "HYD_NEW" in rejected and rejected["HYD_NEW"] == "CHECKLIST_STALE"
    # 任务因未补齐新项仍处于巡检中
    assert body["task_status"] == "IN_PROGRESS"

    # 刷新到 v2 补齐后可正常提交
    resp2 = client.post(
        f"/api/inspection-result/task/{task_id}/submit",
        headers=hi,
        json={"checklist_version": "v2",
              "items": [{"device_id": device_id, "item_code": "HYD_NEW", "result_status": "NORMAL"}]},
    )
    assert resp2.json()["task_status"] == "SUBMITTED"
    assert resp2.json()["rejected"] == []


def test_unknown_item_rejected(client, auth):
    hi = auth("inspector")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)
    chk = client.get(f"/api/inspection-task/{task_id}/checklist", headers=hi).json()
    device_id = client.get(f"/api/fire-device?building_id={chk['task']['building_id']}", headers=hi).json()[0]["id"]
    resp = client.post(
        f"/api/inspection-result/task/{task_id}/submit",
        headers=hi,
        json={"checklist_version": chk["current_version"],
              "items": [{"device_id": device_id, "item_code": "NOT_EXIST", "result_status": "NORMAL"}]},
    )
    assert resp.json()["rejected"][0]["reason_code"] == "CHECKLIST_ITEM_UNKNOWN"
