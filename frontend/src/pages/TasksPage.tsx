import { useEffect, useMemo, useState } from "react";
import {
  bumpChecklistVersion,
  claimInspectionTask,
  createInspectionTask,
  listInspectionTask,
  reviewInspectionTask,
  submitInspectionTask
} from "../api/InspectionTask";
import { submitInspectionResults } from "../api/InspectionResult";
import { ChecklistPanel } from "../components/common/ChecklistPanel";
import { ConflictList } from "../components/common/ConflictList";
import { EmptyState } from "../components/common/EmptyState";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceType } from "../constants/DeviceType";
import { HazardSeverity } from "../constants/HazardSeverity";
import { useChecklistProgress } from "../hooks/useChecklistProgress";
import { useAuthStore } from "../stores/AuthStore";
import { useBuildingStore } from "../stores/BuildingStore";
import type { ChecklistItem, InspectionTask } from "../types/InspectionTask";
import type { ResultConflict, SubmitResultItem } from "../types/InspectionResult";
import {
  formatDate,
  formatDeviceType,
  formatInspectionStatus
} from "../utils/formatters";

interface DraftRow {
  result_status: "NORMAL" | "ABNORMAL";
  measured_value: string;
  note: string;
  severity: string;
}

const emptyDraft: DraftRow = {
  result_status: "NORMAL",
  measured_value: "",
  note: "",
  severity: "MEDIUM"
};

export function TasksPage() {
  const user = useAuthStore((state) => state.user);
  const buildings = useBuildingStore((state) => state.rows);
  const loadBuildings = useBuildingStore((state) => state.load);

  const [tasks, setTasks] = useState<InspectionTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [buildingFilter, setBuildingFilter] = useState<number | undefined>(undefined);
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [drafts, setDrafts] = useState<Record<string, DraftRow>>({});
  const [conflicts, setConflicts] = useState<ResultConflict[]>([]);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  // 排期表单
  const [planBuilding, setPlanBuilding] = useState<number | "">("");
  const [planType, setPlanType] = useState<string>("HYDRANT");

  const isInspector = user?.role === "INSPECTOR";
  const isSupervisor = user?.role === "SUPERVISOR";

  async function reload() {
    setLoading(true);
    setError("");
    try {
      const rows = await listInspectionTask({
        buildingId: buildingFilter,
        status: statusFilter || undefined
      });
      setTasks(rows);
      if (selectedId) {
        const updated = rows.find((t) => t.id === selectedId);
        if (updated) setSelectedTask(updated);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const [selectedTask, setSelectedTask] = useState<InspectionTask | null>(null);

  useEffect(() => {
    void loadBuildings();
  }, [loadBuildings]);

  useEffect(() => {
    void reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [buildingFilter, statusFilter]);

  const progress = useChecklistProgress(selectedTask?.items ?? []);

  const canEdit = useMemo(
    () =>
      !!selectedTask &&
      selectedTask.status === "IN_PROGRESS" &&
      selectedTask.inspector_id === user?.id,
    [selectedTask, user]
  );

  function selectTask(task: InspectionTask) {
    setSelectedId(task.id);
    setSelectedTask(task);
    setConflicts([]);
    setNotice("");
    setError("");
    const initial: Record<string, DraftRow> = {};
    for (const item of task.items) {
      initial[item.item_code] = item.result_status
        ? {
            result_status: item.result_status,
            measured_value: item.measured_value,
            note: item.note,
            severity: "MEDIUM"
          }
        : { ...emptyDraft };
    }
    setDrafts(initial);
  }

  function updateDraft(itemCode: string, patch: Partial<DraftRow>) {
    setDrafts((prev) => ({ ...prev, [itemCode]: { ...prev[itemCode], ...patch } }));
  }

  async function safeCall(fn: () => Promise<unknown>, success?: string) {
    setError("");
    setNotice("");
    try {
      await fn();
      if (success) setNotice(success);
      await reload();
      return true;
    } catch (err) {
      setError((err as Error).message);
      return false;
    }
  }

  async function onClaim(taskId: number) {
    await safeCall(() => claimInspectionTask(taskId), "领取成功，请逐项填写检查项");
  }

  async function onBumpVersion() {
    if (!selectedTask) return;
    await safeCall(
      () => bumpChecklistVersion(selectedTask.id),
      "清单版本已升级，使用旧版本的提交将被拒绝"
    );
  }

  async function onSubmitItem(item: ChecklistItem) {
    if (!selectedTask) return;
    const draft = drafts[item.item_code] ?? emptyDraft;
    const payload: SubmitResultItem = {
      item_code: item.item_code,
      checklist_version: selectedTask.checklist_version,
      result_status: draft.result_status,
      measured_value: draft.measured_value,
      note: draft.note,
      severity: draft.result_status === "ABNORMAL" ? draft.severity : undefined
    };
    setError("");
    try {
      const res = await submitInspectionResults(selectedTask.id, [payload]);
      setConflicts(res.conflicts);
      setSelectedTask(res.task);
      setSelectedId(res.task.id);
      if (res.saved.length > 0) setNotice(`检查项已保存（${res.saved[0].result_status === "ABNORMAL" ? "异常，已生成/更新隐患单" : "正常"}）`);
      await reload();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function onSubmitTask() {
    if (!selectedTask) return;
    const ok = await safeCall(
      () => submitInspectionTask(selectedTask.id),
      "已提交主管复验"
    );
    if (ok) {
      // reload 会刷新选中任务
    }
  }

  async function onReview() {
    if (!selectedTask) return;
    await safeCall(() => reviewInspectionTask(selectedTask.id, "复验合格"), "巡检任务已复验关闭");
  }

  async function onCreatePlan() {
    if (!planBuilding) return;
    await safeCall(
      () => createInspectionTask({ building_id: Number(planBuilding), task_type: planType }),
      "排期成功，已按该楼栋设备生成巡检清单"
    );
  }

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>巡检任务</h1>
        </div>
        <div className="head-meta">
          {selectedTask ? (
            <StatusBadge value={selectedTask.status} />
          ) : null}
        </div>
      </section>

      {isSupervisor ? (
        <section className="panel create-bar">
          <strong>按楼栋排期</strong>
          <select value={planBuilding} onChange={(e) => setPlanBuilding(e.target.value ? Number(e.target.value) : "")}>
            <option value="">选择楼栋</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
          <select value={planType} onChange={(e) => setPlanType(e.target.value)}>
            {DeviceType.map((t) => (
              <option key={t} value={t}>{formatDeviceType(t)}</option>
            ))}
          </select>
          <button className="btn btn-primary" disabled={!planBuilding} onClick={onCreatePlan}>
            创建巡检任务
          </button>
        </section>
      ) : null}

      <section className="filter-bar panel">
        <label>
          楼栋
          <select
            value={buildingFilter ?? ""}
            onChange={(e) => setBuildingFilter(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">全部楼栋</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </label>
        <label>
          状态
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">全部状态</option>
            {["PLANNED", "IN_PROGRESS", "SUBMITTED", "REVIEWED", "OVERDUE"].map((s) => (
              <option key={s} value={s}>{formatInspectionStatus(s)}</option>
            ))}
          </select>
        </label>
      </section>

      {error ? <p className="form-error">{error}</p> : null}
      {notice ? <p className="form-notice">{notice}</p> : null}
      <ConflictList conflicts={conflicts} />

      <section className="workbench task-layout">
        <div className="panel">
          <h2>任务列表（{tasks.length}）{loading ? " 加载中…" : ""}</h2>
          {tasks.length === 0 ? <EmptyState title="暂无巡检任务" /> : (
            <ul className="task-list">
              {tasks.map((task) => (
                <li
                  key={task.id}
                  className={`task-item ${selectedTask?.id === task.id ? "selected" : ""}`}
                  onClick={() => selectTask(task)}
                >
                  <div>
                    <strong>#{task.id} {task.building_name}</strong>
                    <span className="muted">
                      {formatDeviceType(task.task_type)} · {task.submitted_items}/{task.total_items} 项
                      {task.inspector_name ? ` · ${task.inspector_name}` : " · 待领取"}
                    </span>
                  </div>
                  <StatusBadge value={task.status} />
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel wide">
          {!selectedTask ? (
            <EmptyState title="选择左侧任务查看巡检清单" hint="巡检员领取任务后可逐项提交结果" />
          ) : (
            <>
              <div className="detail-head">
                <div>
                  <h2>
                    #{selectedTask.id} {selectedTask.building_name} ·{" "}
                    {formatDeviceType(selectedTask.task_type)}
                  </h2>
                  <span className="muted">
                    计划日期 {formatDate(selectedTask.plan_date)} · 领取人{" "}
                    {selectedTask.inspector_name || "—"}
                  </span>
                </div>
                <div className="action-group">
                  {isInspector && selectedTask.status === "PLANNED" ? (
                    <button className="btn btn-primary" onClick={() => onClaim(selectedTask.id)}>
                      领取任务
                    </button>
                  ) : null}
                  {isInspector && canEdit ? (
                    <button
                      className="btn btn-primary"
                      disabled={progress.remaining > 0}
                      title={progress.remaining > 0 ? `还差 ${progress.remaining} 项未提交` : ""}
                      onClick={onSubmitTask}
                    >
                      提交复核（{progress.submitted}/{progress.total}）
                    </button>
                  ) : null}
                  {isSupervisor && selectedTask.status === "SUBMITTED" ? (
                    <button className="btn btn-primary" onClick={onReview}>
                      复验关闭
                    </button>
                  ) : null}
                  {isSupervisor && selectedTask.status === "IN_PROGRESS" ? (
                    <button className="btn btn-ghost" onClick={onBumpVersion}>
                      升级清单版本（当前 v{selectedTask.checklist_version}）
                    </button>
                  ) : null}
                </div>
              </div>

              <ChecklistPanel
                items={selectedTask.items}
                version={selectedTask.checklist_version}
                renderItem={(item) => (
                  <ChecklistEditor
                    key={item.id}
                    item={item}
                    draft={drafts[item.item_code] ?? emptyDraft}
                    editable={canEdit}
                    onChange={(patch) => updateDraft(item.item_code, patch)}
                    onSubmit={() => onSubmitItem(item)}
                  />
                )}
              />
            </>
          )}
        </div>
      </section>
    </main>
  );
}

function ChecklistEditor({
  item,
  draft,
  editable,
  onChange,
  onSubmit
}: {
  item: ChecklistItem;
  draft: DraftRow;
  editable: boolean;
  onChange: (patch: Partial<DraftRow>) => void;
  onSubmit: () => void;
}) {
  const submitted = item.result_status !== null;
  return (
    <div className="checklist-editor">
      <div className="checklist-editor-head">
        <div>
          <strong>{item.item_name}</strong>
          <span className="muted">
            {item.item_code} · v{item.checklist_version}
            {submitted ? ` · 已由 ${item.submitted_by_name || "巡检员"} 提交` : ""}
          </span>
        </div>
        {submitted ? <StatusBadge value={item.result_status ?? "NORMAL"} /> : null}
        {item.hazard_id && item.hazard_status !== "CLOSED" ? (
          <StatusBadge value={item.hazard_status ?? "OPEN"} />
        ) : null}
      </div>
      <div className="checklist-form">
        <label>
          结论
          <select
            value={draft.result_status}
            disabled={!editable}
            onChange={(e) =>
              onChange({ result_status: e.target.value as "NORMAL" | "ABNORMAL" })
            }
          >
            <option value="NORMAL">正常</option>
            <option value="ABNORMAL">异常</option>
          </select>
        </label>
        {draft.result_status === "ABNORMAL" ? (
          <label>
            隐患级别
            <select
              value={draft.severity}
              disabled={!editable}
              onChange={(e) => onChange({ severity: e.target.value })}
            >
              {HazardSeverity.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
        ) : null}
        <input
          placeholder="实测值（如 0.6MPa）"
          value={draft.measured_value}
          disabled={!editable}
          onChange={(e) => onChange({ measured_value: e.target.value })}
        />
        <input
          placeholder="备注/异常描述"
          value={draft.note}
          disabled={!editable}
          onChange={(e) => onChange({ note: e.target.value })}
        />
        {editable ? (
          <button className="btn btn-small btn-primary" onClick={onSubmit}>
            提交本项
          </button>
        ) : (
          <span className="muted">任务提交后不可修改</span>
        )}
      </div>
    </div>
  );
}
