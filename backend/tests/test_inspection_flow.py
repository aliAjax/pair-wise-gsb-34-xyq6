"""巡检处置主流程：领取 → 逐项提交 → 异常开单 → 整改 → 复验关闭 → 设备重算。"""


def _full_items(client, headers, task_id, statuses=None):
    chk = client.get(f"/api/inspection-task/{task_id}/checklist", headers=headers).json()
    building_id = chk["task"]["building_id"]
    device_id = client.get(f"/api/fire-device?building_id={building_id}", headers=headers).json()[0]["id"]
    items = []
    for index, item in enumerate(chk["items"]):
        status = statuses[index] if statuses else ("ABNORMAL" if index == 0 else "NORMAL")
        items.append({"device_id": device_id, "item_code": item["item_code"], "result_status": status, "note": "测试"})
    return device_id, chk["current_version"], items


def test_full_inspection_to_close_flow(client, auth):
    hi = auth("inspector")
    hm = auth("maintainer")
    hs = auth("supervisor")

    tasks = client.get("/api/inspection-task", headers=hi).json()
    task_id = tasks[0]["id"]
    assert client.post(f"/api/inspection-task/{task_id}/claim", headers=hi).status_code == 200

    device_id, version, items = _full_items(client, hi, task_id)
    resp = client.post(
        f"/api/inspection-result/task/{task_id}/submit",
        headers=hi,
        json={"checklist_version": version, "items": items},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["task_status"] == "SUBMITTED"
    assert body["all_items_completed"] is True
    assert body["rejected"] == []

    # 异常项生成隐患单；设备立即变故障
    tickets = client.get("/api/hazard-ticket", headers=hs).json()
    assert any(t["device_id"] == device_id for t in tickets)
    device = [d for d in client.get("/api/fire-device", headers=hs).json() if d["id"] == device_id][0]
    assert device["status"] == "FAULT"

    ticket = [t for t in tickets if t["device_id"] == device_id][0]
    ticket_id = ticket["id"]
    assert client.post(f"/api/hazard-ticket/{ticket_id}/assign", headers=hs,
                       json={"owner_id": 3, "severity": "HIGH", "deadline": "2026-10-20"}).status_code == 200
    device = [d for d in client.get("/api/fire-device", headers=hs).json() if d["id"] == device_id][0]
    assert device["status"] == "MAINTAINING"

    assert client.post(f"/api/hazard-ticket/{ticket_id}/rectify", headers=hm,
                       json={"rectify_note": "已更换"}).status_code == 200
    assert client.post(f"/api/hazard-ticket/{ticket_id}/review", headers=hs,
                       json={"approved": True, "rectify_note": "合格"}).status_code == 200

    ticket = [t for t in client.get("/api/hazard-ticket", headers=hs).json() if t["id"] == ticket_id][0]
    assert ticket["rectify_status"] == "CLOSED"
    assert ticket["closed_at"]
    device = [d for d in client.get("/api/fire-device", headers=hs).json() if d["id"] == device_id][0]
    assert device["status"] == "NORMAL"

    overview = client.get("/api/dashboard/overview", headers=hs).json()
    assert overview["open_ticket_count"] == 0
    assert overview["device_status_distribution"].get("FAULT", 0) == 0


def test_review_rejection_reopens_rectification(client, auth):
    hi, hm, hs = auth("inspector"), auth("maintainer"), auth("supervisor")
    task_id = client.get("/api/inspection-task", headers=hi).json()[0]["id"]
    client.post(f"/api/inspection-task/{task_id}/claim", headers=hi)
    device_id, version, items = _full_items(client, hi, task_id)
    client.post(f"/api/inspection-result/task/{task_id}/submit", headers=hi,
                json={"checklist_version": version, "items": items})
    ticket_id = [t for t in client.get("/api/hazard-ticket", headers=hs).json() if t["device_id"] == device_id][0]["id"]
    client.post(f"/api/hazard-ticket/{ticket_id}/assign", headers=hs, json={"owner_id": 3})
    client.post(f"/api/hazard-ticket/{ticket_id}/rectify", headers=hm, json={"rectify_note": "处理"})
    assert client.post(f"/api/hazard-ticket/{ticket_id}/review", headers=hs,
                       json={"approved": False, "rectify_note": "仍渗漏"}).status_code == 200
    ticket = [t for t in client.get("/api/hazard-ticket", headers=hs).json() if t["id"] == ticket_id][0]
    assert ticket["rectify_status"] == "REJECTED"
    assert ticket["closed_at"] is None
    # 退回后可再次整改并关闭
    client.post(f"/api/hazard-ticket/{ticket_id}/rectify", headers=hm, json={"rectify_note": "二次处理"})
    assert client.post(f"/api/hazard-ticket/{ticket_id}/review", headers=hs,
                       json={"approved": True}).status_code == 200
