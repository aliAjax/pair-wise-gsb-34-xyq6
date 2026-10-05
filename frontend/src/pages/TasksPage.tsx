import { useEffect, useMemo, useState } from "react";
import {
  claimInspectionTask,
  createInspectionTask,
  getTaskChecklist,
  publishChecklist,
  reviewInspectionTask,
} from "../api/InspectionTask";
import { submitInspectionResults, listInspectionResult } from "../api/InspectionResult";
import { AlertBanner } from "../components/common/AlertBanner";
import { ChecklistPanel } from "../components/common/ChecklistPanel";
import { EmptyState } from "../components/common/EmptyState";
import { Modal } from "../components/common/Modal";
import { PageHeader } from "../components/common/PageHeader";
import { StatusBadge, statusTone } from "../components/common/StatusBadge";
import { DeviceType } from "../constants/DeviceType";
import { ROLE_INSPECTOR, ROLE_SUPERVISOR } from "../constants/Role";
import { useBuildingStore } from "../stores/BuildingStore";
import { useAuthStore } from "../stores/AuthStore";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { useInspectionTaskStore } from "../stores/InspectionTaskStore";
import type { ChecklistDetail, SubmitResultItem } from "../types/InspectionTask";
import { formatDeviceType, formatInspectionStatus } from "../utils/formatters";

type DraftRow = {
  device_id: number | "";
  result_status: "NORMAL" | "ABNORMAL" | "";
  measured_value: string;
  note: string;
};

export function TasksPage() {
  const user = useAuthStore((state) => state.user);
  const role = user?.role;
  const buildings = useBuildingStore((state) => state.rows);
  const loadBuildings = useBuildingStore((state) => state.load);
  const tasks = useInspectionTaskStore((state) => state.rows);
  const loadTasks = useInspectionTaskStore((state) => state.load);
  const devices = useFireDeviceStore((state) => state.rows);
  const loadDevices = useFireDeviceStore((state) => state.load);

  const [buildingFilter, setBuildingFilter] = useState<number | undefined>(undefined);
  const [notice, setNotice] = useState<{ tone: "success" | "warn" | "danger"; text: string } | null>(null);
  const [checklist, setChecklist] = useState<ChecklistDetail | null>(null);
  const [clientVersion, setClientVersion] = useState("v1");
  const [drafts, setDrafts] = useState<Record<string, DraftRow>>({});
  const [submitting, setSubmitting] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [publishOpen, setPublishOpen] = useState(false);
  const [createForm, setCreateForm] = useState({ building_id: "", plan_date: "2026-10-10", task_type: "EXTINGUISHER" });
  const [publishForm, setPublishForm] = useState({ task_type: "EXTINGUISHER", item_codes: "EXT_PRESSURE\nEXT_QUALITY\nEXT_EXPIRE\nEXT_NEW" });

  useEffect(() => {
    loadBuildings();
    loadTasks();
    loadDevices();
  }, [loadBuildings, loadTasks, loadDevices]);

  const buildingMap = useMemo(() => new Map(buildings.map((row) => [row.id, row.name])), [buildings]);
  const visibleTasks = useMemo(
    () => tasks.filter((task) => buildingFilter === undefined || task.building_id === buildingFilter),
    [tasks, buildingFilter],
  );

  const refreshAll = () => {
    loadTasks();
    loadDevices();
  };

  const openChecklist = async (taskId: number) => {
    setNotice(null);
    const [detail, savedResults] = await Promise.all([
      getTaskChecklist(taskId),
      listInspectionResult({ task_id: taskId }).catch(() => []),
    ]);
    setChecklist(detail);
    setClientVersion(detail.current_version);
    const resultByCode = new Map(savedResults.map((row) => [row.item_code, row]));
    const next: Record<string, DraftRow> = {};
    detail.items.forEach((item) => {
      const saved = resultByCode.get(item.item_code);
      // 已填项带出设备/结果/测量值，支持补录或覆盖；未填项留空。
      next[item.item_code] = saved
        ? {
            device_id: saved.device_id,
            result_status: saved.result_status === "ABNORMAL" ? "ABNORMAL" : "NORMAL",
            measured_value: saved.measured_value ?? "",
            note: saved.note ?? "",
          }
        : { device_id: "", result_status: "", measured_value: "", note: "" };
    });
    setDrafts(next);
  };

  const closeChecklist = () => {
    setChecklist(null);
    setDrafts({});
  };

  const updateDraft = (code: string, patch: Partial<DraftRow>) => {
    setDrafts((prev) => ({ ...prev, [code]: { ...prev[code], ...patch } }));
  };

  const handleClaim = async (taskId: number) => {
    setNotice(null);
    try {
      await claimInspectionTask(taskId);
      setNotice({ tone: "success", text: "领取成功，可逐项填写巡检结果" });
      await loadTasks();
      await openChecklist(taskId);
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    }
  };

  const handleSubmit = async () => {
    if (!checklist) return;
    const activeItems = checklist.items.filter((item) => !item.deprecated);
    const payload: SubmitResultItem[] = [];
    for (const item of activeItems) {
      const draft = drafts[item.item_code];
      if (!draft || !draft.result_status) continue;
      if (!draft.device_id) {
        setNotice({ tone: "warn", text: `检查项 ${item.item_code} 还未选择对应设备` });
        return;
      }
      payload.push({
        device_id: Number(draft.device_id),
        item_code: item.item_code,
        result_status: draft.result_status,
        measured_value: draft.measured_value || null,
        note: draft.note || null,
      });
    }
    if (payload.length === 0) {
      setNotice({ tone: "warn", text: "请至少为一个检查项选择合格/异常并选择设备" });
      return;
    }
    setSubmitting(true);
    setNotice(null);
    try {
      const res = await submitInspectionResults(checklist.task.id, clientVersion, payload);
      if (res.rejected.length > 0) {
        const staleItems = res.rejected.filter((row) => row.reason_code === "CHECKLIST_STALE");
        setNotice({
          tone: staleItems.length ? "warn" : "danger",
          text: `已保存 ${res.saved.length} 项；${res.rejected.length} 项被拒绝：${res.rejected
            .slice(0, 3)
            .map((row) => row.reason)
            .join("；")}`,
        });
      } else if (res.all_items_completed) {
        setNotice({ tone: "success", text: "巡检结果全部提交，任务进入待复验，异常项已自动生成隐患单" });
      } else {
        setNotice({ tone: "success", text: `已保存 ${res.saved.length} 项，剩余检查项可继续补录` });
      }
      await openChecklist(checklist.task.id);
      refreshAll();
      if (res.all_items_completed && res.rejected.length === 0) {
        // 完成后保留弹窗展示最终状态；不强制关闭。
      }
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    } finally {
      setSubmitting(false);
    }
  };

  const handleReview = async (taskId: number, approved: boolean) => {
    setNotice(null);
    try {
      await reviewInspectionTask(taskId, approved);
      setNotice({ tone: "success", text: approved ? "任务已复核通过" : "任务已退回，巡检员可补充结果" });
      await loadTasks();
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    }
  };

  const handleCreate = async () => {
    try {
      await createInspectionTask({
        building_id: Number(createForm.building_id),
        plan_date: createForm.plan_date,
        task_type: createForm.task_type,
      });
      setCreateOpen(false);
      setNotice({ tone: "success", text: "巡检任务已排期，等待巡检员按楼栋领取" });
      await loadTasks();
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    }
  };

  const handlePublish = async () => {
    try {
      const items = publishForm.item_codes
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((code) => ({ item_code: code, item_name: code }));
      const res = await publishChecklist({ task_type: publishForm.task_type, items });
      setPublishOpen(false);
      setNotice({
        tone: "warn",
        text: `已发布清单 ${res.checklist_version}，影响进行中任务：${res.superseded_tasks.length ? res.superseded_tasks.join("、") : "无"}；巡检员旧项将被拒绝并提示刷新`,
      });
      await loadTasks();
      if (checklist) await openChecklist(checklist.task.id);
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    }
  };

  const taskDevices = checklist
    ? devices.filter((device) => device.building_id === checklist.task.building_id)
    : [];
  const resultMap = useMemo(() => {
    if (!checklist) return {};
    const map: Record<string, string> = {};
    checklist.items.forEach((item) => {
      if (item.filled && item.result_status) map[item.item_code] = item.result_status;
    });
    Object.entries(drafts).forEach(([code, draft]) => {
      if (draft.result_status) map[code] = draft.result_status;
    });
    return map;
  }, [checklist, drafts]);

  return (
    <main className="page">
      <PageHeader
        title="巡检任务"
        eyebrow="按楼栋领取 · 逐项提交 · 异常自动开单"
        actions={
          role === ROLE_SUPERVISOR ? (
            <>
              <button className="btn" onClick={() => setPublishOpen(true)}>发布清单新版本</button>
              <button className="btn btn-primary" onClick={() => setCreateOpen(true)}>排期巡检任务</button>
            </>
          ) : undefined
        }
      />
      {notice && (
        <AlertBanner tone={notice.tone} onClose={() => setNotice(null)}>{notice.text}</AlertBanner>
      )}

      <section className="panel filter-bar">
        <label>
          楼栋
          <select value={buildingFilter ?? ""} onChange={(e) => setBuildingFilter(e.target.value ? Number(e.target.value) : undefined)}>
            <option value="">全部楼栋</option>
            {buildings.map((row) => (
              <option key={row.id} value={row.id}>{row.name}</option>
            ))}
          </select>
        </label>
      </section>

      <section className="panel">
        {visibleTasks.length === 0 ? (
          <EmptyState title="暂无巡检任务" hint={role === ROLE_SUPERVISOR ? "点击右上角“排期巡检任务”创建" : undefined} />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>任务</th>
                <th>楼栋</th>
                <th>计划日期</th>
                <th>清单版本</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {visibleTasks.map((task) => {
                const mine = task.inspector_id === user?.id;
                return (
                  <tr key={task.id}>
                    <td>
                      <strong>#{task.id} {formatDeviceType(task.task_type)}巡检</strong>
                      <div className="muted">{task.inspector_id ? `领取人 #${task.inspector_id}` : "待领取"}</div>
                    </td>
                    <td>{buildingMap.get(task.building_id) ?? `#${task.building_id}`}</td>
                    <td>{task.plan_date}</td>
                    <td>
                      <span className={`badge ${task.status === "IN_PROGRESS" ? "tone-warn" : "tone-idle"}`}>{task.checklist_version}</span>
                    </td>
                    <td><StatusBadge value={task.status} label={formatInspectionStatus(task.status)} /></td>
                    <td className="action-cell">
                      {role === ROLE_INSPECTOR && task.status === "PLANNED" && (
                        <button className="btn btn-primary" onClick={() => handleClaim(task.id)}>领取并填报</button>
                      )}
                      {role === ROLE_INSPECTOR && mine && task.status === "IN_PROGRESS" && (
                        <button className="btn btn-primary" onClick={() => openChecklist(task.id)}>继续填报</button>
                      )}
                      {role === ROLE_INSPECTOR && mine && task.status === "SUBMITTED" && (
                        <button className="btn" onClick={() => openChecklist(task.id)}>查看提交</button>
                      )}
                      {role === ROLE_INSPECTOR && !mine && task.inspector_id !== null && (
                        <span className="muted">已被他人领取</span>
                      )}
                      {role === ROLE_SUPERVISOR && (
                        <>
                          <button className="btn" onClick={() => openChecklist(task.id)}>查看清单</button>
                          {task.status === "SUBMITTED" && (
                            <button className="btn btn-primary" onClick={() => handleReview(task.id, true)}>复核通过</button>
                          )}
                        </>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </section>

      <Modal
        title={checklist ? `巡检任务 #${checklist.task.id} 逐项填报` : ""}
        open={!!checklist}
        onClose={closeChecklist}
        footer={
          checklist && role === ROLE_INSPECTOR && checklist.task.inspector_id === user?.id && checklist.task.status === "IN_PROGRESS" ? (
            <>
              <span className={`muted`}>持有的清单版本：{clientVersion}（当前 {checklist.current_version}）</span>
              <button className="btn btn-primary" disabled={submitting} onClick={handleSubmit}>
                {submitting ? "提交中…" : "提交检查项"}
              </button>
            </>
          ) : undefined
        }
      >
        {checklist && (
          <div className="checklist-form">
            <ChecklistPanel
              items={checklist.items}
              resultMap={resultMap}
              version={clientVersion}
              currentVersion={checklist.current_version}
            />
            <table className="data-table checklist-table">
              <thead>
                <tr>
                  <th>检查项</th>
                  <th>对应设备</th>
                  <th>结果</th>
                  <th>测量值 / 备注</th>
                </tr>
              </thead>
              <tbody>
                {checklist.items.map((item) => {
                  if (item.deprecated) {
                    return (
                      <tr key={item.item_code} className="row-stale">
                        <td><s>{item.item_code}</s><div className="danger-text">该旧项已在新版本清单移除，提交会被拒绝</div></td>
                        <td>—</td>
                        <td><span className="badge tone-danger">版本过期</span></td>
                        <td>{item.item_name}</td>
                      </tr>
                    );
                  }
                  const draft = drafts[item.item_code] ?? { device_id: "", result_status: "", measured_value: "", note: "" };
                  const readOnly =
                    checklist.task.status !== "IN_PROGRESS" ||
                    (role === ROLE_INSPECTOR && checklist.task.inspector_id !== user?.id);
                  return (
                    <tr key={item.item_code} className={draft.result_status === "ABNORMAL" ? "row-abnormal" : ""}>
                      <td>
                        <strong>{item.item_code}</strong>
                        <div className="muted">{item.item_name}</div>
                        {item.filled && <span className={`badge tone-${statusTone(item.result_status ?? "")}`}>已填：{item.result_status === "ABNORMAL" ? "异常" : "合格"}</span>}
                      </td>
                      <td>
                        <select
                          value={draft.device_id}
                          disabled={readOnly}
                          onChange={(e) => updateDraft(item.item_code, { device_id: e.target.value ? Number(e.target.value) : "" })}
                        >
                          <option value="">选择设备</option>
                          {taskDevices.map((device) => (
                            <option key={device.id} value={device.id}>
                              {device.device_code} · {device.floor}层 · {device.location_desc}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <div className="radio-stack">
                          <label>
                            <input
                              type="radio"
                              name={`status-${item.item_code}`}
                              checked={draft.result_status === "NORMAL"}
                              disabled={readOnly}
                              onChange={() => updateDraft(item.item_code, { result_status: "NORMAL" })}
                            />
                            合格
                          </label>
                          <label>
                            <input
                              type="radio"
                              name={`status-${item.item_code}`}
                              checked={draft.result_status === "ABNORMAL"}
                              disabled={readOnly}
                              onChange={() => updateDraft(item.item_code, { result_status: "ABNORMAL" })}
                            />
                            异常（自动开隐患单）
                          </label>
                        </div>
                      </td>
                      <td>
                        <input
                          placeholder="测量值，如 1.2MPa"
                          value={draft.measured_value}
                          disabled={readOnly}
                          onChange={(e) => updateDraft(item.item_code, { measured_value: e.target.value })}
                        />
                        <input
                          placeholder="异常描述/备注"
                          value={draft.note}
                          disabled={readOnly}
                          onChange={(e) => updateDraft(item.item_code, { note: e.target.value })}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Modal>

      <Modal
        title="排期巡检任务"
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        footer={<button className="btn btn-primary" onClick={handleCreate}>创建任务</button>}
      >
        <div className="form-stack">
          <label>
            楼栋
            <select value={createForm.building_id} onChange={(e) => setCreateForm({ ...createForm, building_id: e.target.value })}>
              <option value="">选择楼栋</option>
              {buildings.map((row) => (
                <option key={row.id} value={row.id}>{row.name}</option>
              ))}
            </select>
          </label>
          <label>
            计划日期
            <input type="date" value={createForm.plan_date} onChange={(e) => setCreateForm({ ...createForm, plan_date: e.target.value })} />
          </label>
          <label>
            巡检设备类型
            <select value={createForm.task_type} onChange={(e) => setCreateForm({ ...createForm, task_type: e.target.value })}>
              {DeviceType.map((value) => (
                <option key={value} value={value}>{formatDeviceType(value)}</option>
              ))}
            </select>
          </label>
        </div>
      </Modal>

      <Modal
        title="发布清单新版本（进行中任务的旧项将被标记冲突）"
        open={publishOpen}
        onClose={() => setPublishOpen(false)}
        footer={<button className="btn btn-primary" onClick={handlePublish}>发布</button>}
      >
        <div className="form-stack">
          <label>
            设备类型
            <select value={publishForm.task_type} onChange={(e) => setPublishForm({ ...publishForm, task_type: e.target.value })}>
              {DeviceType.map((value) => (
                <option key={value} value={value}>{formatDeviceType(value)}</option>
              ))}
            </select>
          </label>
          <label>
            新版本检查项编号（每行一个；删除的旧项提交时将被拒绝，新增项要求巡检员补检）
            <textarea rows={6} value={publishForm.item_codes} onChange={(e) => setPublishForm({ ...publishForm, item_codes: e.target.value })} />
          </label>
        </div>
      </Modal>
    </main>
  );
}
