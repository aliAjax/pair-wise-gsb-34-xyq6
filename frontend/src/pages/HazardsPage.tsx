import { useEffect, useMemo, useState } from "react";
import {
  assignHazardTicket,
  listHazardTicket,
  rectifyHazardTicket,
  reviewHazardTicket,
} from "../api/HazardTicket";
import { listUsers } from "../api/Auth";
import { AlertBanner } from "../components/common/AlertBanner";
import { DeviceLocationCell } from "../components/common/DeviceLocationCell";
import { EmptyState } from "../components/common/EmptyState";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { Modal } from "../components/common/Modal";
import { PageHeader } from "../components/common/PageHeader";
import { StatusBadge } from "../components/common/StatusBadge";
import { TimelineList } from "../components/common/TimelineList";
import { HAZARD_SEVERITY_OPTIONS } from "../constants/HazardSeverityRef";
import { RectifyStatus, RectifyStatusLabels } from "../constants/RectifyStatus";
import { ROLE_MAINTAINER, ROLE_SUPERVISOR } from "../constants/Role";
import { useAuthStore } from "../stores/AuthStore";
import { useBuildingStore } from "../stores/BuildingStore";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import type { HazardTicket } from "../types/HazardTicket";
import type { User } from "../types/Auth";
import { formatDate, formatRectifyStatus } from "../utils/formatters";
import { useHazardFlow } from "../hooks/useHazardFlow";

export function HazardsPage() {
  const user = useAuthStore((state) => state.user);
  const buildings = useBuildingStore((state) => state.rows);
  const loadBuildings = useBuildingStore((state) => state.load);
  const devices = useFireDeviceStore((state) => state.rows);
  const loadDevices = useFireDeviceStore((state) => state.load);

  const [tickets, setTickets] = useState<HazardTicket[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [notice, setNotice] = useState<{ tone: "success" | "warn" | "danger"; text: string } | null>(null);
  const [selected, setSelected] = useState<HazardTicket | null>(null);
  const [assignOpen, setAssignOpen] = useState(false);
  const [rectifyOpen, setRectifyOpen] = useState(false);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [assignForm, setAssignForm] = useState({ owner_id: "", severity: "HIGH", deadline: "2026-10-20" });
  const [rectifyNote, setRectifyNote] = useState("");
  const [reviewNote, setReviewNote] = useState("");

  const load = useMemo(
    () => () => {
      listHazardTicket(statusFilter ? { rectify_status: statusFilter } : undefined).then(setTickets);
    },
    [statusFilter],
  );

  useEffect(() => {
    loadBuildings();
    loadDevices();
    listUsers().then(setUsers).catch(() => undefined);
  }, [loadBuildings, loadDevices]);

  useEffect(() => {
    load();
  }, [load]);

  const buildingMap = useMemo(() => new Map(buildings.map((row) => [row.id, row.name])), [buildings]);
  const deviceMap = useMemo(() => new Map(devices.map((row) => [row.id, row])), [devices]);
  const maintainers = users.filter((row) => row.role === ROLE_MAINTAINER);
  const userName = (id: number | null) => (id === null ? "未派单" : users.find((row) => row.id === id)?.display_name ?? `#${id}`);

  const refreshSelected = (rows: HazardTicket[]) => {
    if (selected) {
      const next = rows.find((row) => row.id === selected.id);
      if (next) setSelected(next);
    }
  };

  const reload = () =>
    listHazardTicket(statusFilter ? { rectify_status: statusFilter } : undefined).then((rows) => {
      setTickets(rows);
      refreshSelected(rows);
      loadDevices();
    });

  const flow = useHazardFlow(selected, user?.role);

  const openAssign = (ticket: HazardTicket) => {
    setSelected(ticket);
    setAssignForm({ owner_id: String(ticket.owner_id ?? maintainers[0]?.id ?? ""), severity: ticket.severity, deadline: "2026-10-20" });
    setAssignOpen(true);
  };

  const submitAssign = async () => {
    if (!selected) return;
    try {
      await assignHazardTicket(selected.id, {
        owner_id: Number(assignForm.owner_id),
        severity: assignForm.severity,
        deadline: assignForm.deadline,
      });
      setAssignOpen(false);
      setNotice({ tone: "success", text: "隐患单已派单，设备进入整改中" });
      await reload();
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    }
  };

  const submitRectify = async () => {
    if (!selected) return;
    if (!rectifyNote.trim()) {
      setNotice({ tone: "warn", text: "请填写整改说明" });
      return;
    }
    try {
      await rectifyHazardTicket(selected.id, rectifyNote.trim());
      setRectifyOpen(false);
      setNotice({ tone: "success", text: "整改说明已提交，等待主管复验" });
      await reload();
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    }
  };

  const submitReview = async (approved: boolean) => {
    if (!selected) return;
    try {
      await reviewHazardTicket(selected.id, approved, reviewNote.trim() || undefined);
      setReviewOpen(false);
      setNotice({
        tone: approved ? "success" : "warn",
        text: approved ? "复验通过，隐患单关闭，设备状态已恢复重算" : "复验不通过，已退回维保人员重新整改",
      });
      await reload();
    } catch (err) {
      setNotice({ tone: "danger", text: (err as Error).message });
    }
  };

  return (
    <main className="page">
      <PageHeader title="隐患整改" eyebrow="异常巡检自动开单 · 派单 → 整改 → 复验关闭" />
      {notice && <AlertBanner tone={notice.tone} onClose={() => setNotice(null)}>{notice.text}</AlertBanner>}

      <section className="panel filter-bar">
        <label>
          整改状态
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">全部状态</option>
            {RectifyStatus.map((value) => (
              <option key={value} value={value}>{RectifyStatusLabels[value]}</option>
            ))}
          </select>
        </label>
        <span className="muted">维保人员仅能看到自己可处理的动作；派单与复验仅主管可操作</span>
      </section>

      <section className="workbench hazards-layout">
        <div className="panel">
          {tickets.length === 0 ? (
            <EmptyState title="暂无隐患单" hint="巡检中提交“异常”检查项后将自动生成" />
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>隐患单</th>
                  <th>级别</th>
                  <th>责任人</th>
                  <th>期限</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((ticket) => {
                  const device = deviceMap.get(ticket.device_id);
                  return (
                    <tr key={ticket.id} className={selected?.id === ticket.id ? "row-selected" : ""}>
                      <td>
                        <button className="link-btn" onClick={() => setSelected(ticket)}>
                          <strong>隐患单 #{ticket.id}</strong>
                        </button>
                        <div className="muted">
                          {device ? (
                            <DeviceLocationCell device={device} buildingName={device ? buildingMap.get(device.building_id) : undefined} />
                          ) : (
                            `设备 #${ticket.device_id}`
                          )}
                        </div>
                      </td>
                      <td><HazardSeverityTag value={ticket.severity} /></td>
                      <td>{userName(ticket.owner_id)}</td>
                      <td>{formatDate(ticket.deadline)}</td>
                      <td><StatusBadge value={ticket.rectify_status} label={formatRectifyStatus(ticket.rectify_status)} /></td>
                      <td className="action-cell">
                        <TicketActions
                          ticket={ticket}
                          currentUserId={user?.id}
                          onAssign={() => openAssign(ticket)}
                          onRectify={() => {
                            setSelected(ticket);
                            setRectifyNote(ticket.rectify_note ?? "");
                            setRectifyOpen(true);
                          }}
                          onReview={() => {
                            setSelected(ticket);
                            setReviewNote("");
                            setReviewOpen(true);
                          }}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        <aside className="panel hazard-detail">
          <h2>处置轨迹</h2>
          {selected ? (
            <>
              <div className="detail-block">
                <div>隐患单 #{selected.id} · 结果 #{selected.result_id}</div>
                <p className="muted">
                  设备：{deviceMap.get(selected.device_id)?.device_code ?? `#${selected.device_id}`}
                </p>
                <p>整改说明：{selected.rectify_note || "—"}</p>
                <p className="muted">关闭时间：{formatDate(selected.closed_at)}</p>
              </div>
              <TimelineList
                items={[
                  {
                    id: "create",
                    title: "巡检异常自动开单",
                    detail: `级别 ${selected.severity}，关联结果 #${selected.result_id}`,
                    tone: "danger",
                  },
                  ...(selected.owner_id
                    ? [{ id: "assign", title: `主管派单给 ${userName(selected.owner_id)}`, detail: selected.deadline ? `期限 ${selected.deadline}` : null, tone: "warn" }]
                    : []),
                  ...(selected.rectify_note
                    ? [{ id: "rectify", title: "维保提交整改说明", detail: selected.rectify_note, tone: "progress" }]
                    : []),
                  ...(selected.rectify_status === "REJECTED"
                    ? [{ id: "reject", title: "主管复验退回", detail: selected.rectify_note, tone: "danger" }]
                    : []),
                  ...(selected.rectify_status === "CLOSED"
                    ? [{ id: "close", title: "主管复验关闭，设备恢复", detail: selected.closed_at, time: selected.closed_at, tone: "ok" }]
                    : []),
                ]}
              />
              <div className="detail-actions">
                {flow.canAssign && <button className="btn btn-primary" onClick={() => openAssign(selected)}>派单</button>}
                {flow.canRectify && selected.owner_id === user?.id && (
                  <button className="btn btn-primary" onClick={() => { setRectifyNote(selected.rectify_note ?? ""); setRectifyOpen(true); }}>
                    提交整改
                  </button>
                )}
                {flow.canReview && (
                  <>
                    <button className="btn" onClick={() => { setReviewNote(""); setReviewOpen(true); }}>复验退回</button>
                    <button className="btn btn-primary" onClick={() => submitReview(true)}>复验通过关闭</button>
                  </>
                )}
                {flow.isClosed && <StatusBadge value="CLOSED" label="已闭环" />}
              </div>
            </>
          ) : (
            <EmptyState title="选择左侧隐患单查看处置轨迹" />
          )}
        </aside>
      </section>

      <Modal
        title="主管派单"
        open={assignOpen}
        onClose={() => setAssignOpen(false)}
        footer={<button className="btn btn-primary" onClick={submitAssign}>确认派单</button>}
      >
        <div className="form-stack">
          <label>
            维保责任人
            <select value={assignForm.owner_id} onChange={(e) => setAssignForm({ ...assignForm, owner_id: e.target.value })}>
              <option value="">选择维保人员</option>
              {maintainers.map((row) => (
                <option key={row.id} value={row.id}>{row.display_name}（{row.username}）</option>
              ))}
            </select>
          </label>
          <label>
            隐患级别
            <select value={assignForm.severity} onChange={(e) => setAssignForm({ ...assignForm, severity: e.target.value })}>
              {HAZARD_SEVERITY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
          <label>
            整改期限
            <input type="date" value={assignForm.deadline} onChange={(e) => setAssignForm({ ...assignForm, deadline: e.target.value })} />
          </label>
        </div>
      </Modal>

      <Modal
        title="维保人员提交整改"
        open={rectifyOpen}
        onClose={() => setRectifyOpen(false)}
        footer={<button className="btn btn-primary" onClick={submitRectify}>提交整改说明</button>}
      >
        <div className="form-stack">
          <label>
            整改措施与结果说明
            <textarea rows={5} value={rectifyNote} onChange={(e) => setRectifyNote(e.target.value)} placeholder="如：已更换失效压力表，复测压力 1.3MPa，铅封完好" />
          </label>
        </div>
      </Modal>

      <Modal
        title="主管复验"
        open={reviewOpen}
        onClose={() => setReviewOpen(false)}
        footer={
          <>
            <button className="btn" onClick={() => submitReview(false)}>复验不通过，退回</button>
            <button className="btn btn-primary" onClick={() => submitReview(true)}>复验通过并关闭</button>
          </>
        }
      >
        <div className="form-stack">
          <p className="muted">复验通过后隐患单关闭，设备状态将按剩余隐患重新计算；不通过则退回维保人员重新整改。</p>
          <label>
            复验意见
            <textarea rows={4} value={reviewNote} onChange={(e) => setReviewNote(e.target.value)} placeholder="填写复验结论（可选）" />
          </label>
        </div>
      </Modal>
    </main>
  );
}

function TicketActions({ ticket, currentUserId, onAssign, onRectify, onReview }: {
  ticket: HazardTicket;
  currentUserId?: number;
  onAssign: () => void;
  onRectify: () => void;
  onReview: () => void;
}) {
  const role = useAuthStore((state) => state.user?.role);
  const status = ticket.rectify_status;
  return (
    <>
      {role === ROLE_SUPERVISOR && (status === "OPEN" || status === "REJECTED") && (
        <button className="btn btn-primary" onClick={onAssign}>派单</button>
      )}
      {role === ROLE_MAINTAINER && (status === "ASSIGNED" || status === "REJECTED") && ticket.owner_id === currentUserId && (
        <button className="btn btn-primary" onClick={onRectify}>整改</button>
      )}
      {role === ROLE_SUPERVISOR && status === "RECTIFIED" && (
        <button className="btn btn-primary" onClick={onReview}>复验</button>
      )}
      {status === "CLOSED" && <span className="muted">已闭环</span>}
    </>
  );
}
