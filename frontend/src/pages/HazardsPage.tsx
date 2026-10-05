import { useEffect, useMemo, useState } from "react";
import {
  assignHazardTicket,
  closeHazardTicket,
  listHazardTicket,
  rectifyHazardTicket
} from "../api/HazardTicket";
import { EmptyState } from "../components/common/EmptyState";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { StatusBadge } from "../components/common/StatusBadge";
import { TimelineList, type TimelineEntry } from "../components/common/TimelineList";
import { HazardSeverity } from "../constants/HazardSeverity";
import { useHazardFlow } from "../hooks/useHazardFlow";
import { useAuthStore } from "../stores/AuthStore";
import type { HazardTicket } from "../types/HazardTicket";
import { formatDate } from "../utils/formatters";

export function HazardsPage() {
  const user = useAuthStore((state) => state.user);
  const isSupervisor = user?.role === "SUPERVISOR";
  const isMaintainer = user?.role === "MAINTAINER";

  const [rows, setRows] = useState<HazardTicket[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [rectifyNote, setRectifyNote] = useState("");
  const [reviewNote, setReviewNote] = useState("");
  // 主管派单固定演示责任人 maintainer_a（id=3）；实际可从用户目录选择
  const [ownerId] = useState(3);

  async function reload() {
    const data = await listHazardTicket({
      rectifyStatus: statusFilter || undefined,
      ownerId: isMaintainer && user ? user.id : undefined
    });
    setRows(data);
    return data;
  }

  useEffect(() => {
    setError("");
    reload().catch((err) => setError((err as Error).message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const flow = useHazardFlow(rows);
  const selected = useMemo(
    () => rows.find((r) => r.id === selectedId) ?? null,
    [rows, selectedId]
  );

  async function safeCall(fn: () => Promise<unknown>, message: string) {
    setError("");
    try {
      await fn();
      setNotice(message);
      const data = await reload();
      const refreshed = data.find((r) => r.id === selectedId);
      if (refreshed) setSelectedId(refreshed.id);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  const timeline: TimelineEntry[] = useMemo(() => {
    if (!selected) return [];
    const entries: TimelineEntry[] = [
      {
        key: "create",
        title: "巡检异常生成隐患单",
        time: formatDate(selected.created_at),
        description: selected.result_note,
        badge: <HazardSeverityTag value={selected.severity} />
      }
    ];
    if (selected.owner_id) {
      entries.push({
        key: "assign",
        title: `派单给 ${selected.owner_name}`,
        time: selected.deadline ? `整改期限 ${formatDate(selected.deadline)}` : null
      });
    }
    if (selected.rectified_at || ["RECTIFIED", "CLOSED"].includes(selected.rectify_status)) {
      entries.push({
        key: "rectify",
        title: "维保人员完成整改",
        time: formatDate(selected.rectified_at),
        description: selected.rectify_note
      });
    }
    if (selected.rectify_status === "CLOSED") {
      entries.push({
        key: "close",
        title: "主管复验通过关闭",
        time: formatDate(selected.closed_at)
      });
    }
    return entries;
  }, [selected]);

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>隐患整改</h1>
        </div>
      </section>

      <section className="metrics metrics-compact">
        {flow.stages.map((stage) => (
          <div className="stat" key={stage.key}>
            <span>{stage.label}</span>
            <strong>{stage.count}</strong>
          </div>
        ))}
        <div className="stat stat-danger">
          <span>逾期</span>
          <strong>{flow.overdueCount}</strong>
        </div>
      </section>

      <section className="filter-bar panel">
        <label>
          整改状态
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">全部</option>
            {["OPEN", "ASSIGNED", "RECTIFIED", "CLOSED"].map((s) => (
              <option key={s} value={s}>
                {s === "OPEN" && "待派单"}{s === "ASSIGNED" && "待整改"}
                {s === "RECTIFIED" && "待复验"}{s === "CLOSED" && "已关闭"}
              </option>
            ))}
          </select>
        </label>
        {isMaintainer ? <span className="muted">仅显示派给我的隐患单</span> : null}
      </section>

      {error ? <p className="form-error">{error}</p> : null}
      {notice ? <p className="form-notice">{notice}</p> : null}

      <section className="workbench">
        <div className="panel wide">
          <h2>隐患单列表（{rows.length}）</h2>
          {rows.length === 0 ? <EmptyState title="暂无隐患单" /> : (
            <div className="table">
              {rows.map((ticket) => (
                <article
                  key={ticket.id}
                  className={`row clickable ${selectedId === ticket.id ? "selected" : ""}`}
                  onClick={() => {
                    setSelectedId(ticket.id);
                    setError("");
                    setNotice("");
                  }}
                >
                  <div>
                    <strong>#{ticket.id} {ticket.building_name} · {ticket.device_code}</strong>
                    <span className="muted">{ticket.item_name}（{ticket.item_code}）</span>
                  </div>
                  <HazardSeverityTag value={ticket.severity} />
                  <StatusBadge value={ticket.rectify_status} />
                  <span className={ticket.overdue ? "text-danger" : "muted"}>
                    {ticket.owner_name || "待派单"} · {formatDate(ticket.deadline)}
                    {ticket.overdue ? " · 逾期" : ""}
                  </span>
                </article>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <h2>处置与流转</h2>
          {!selected ? (
            <EmptyState title="选择左侧隐患单进行处置" />
          ) : (
            <div className="hazard-detail">
              <p>{selected.result_note || "巡检员未填写异常描述"}</p>
              <TimelineList entries={timeline} />
              <div className="hazard-actions">
                {isSupervisor && selected.rectify_status === "OPEN" ? (
                  <SupervisorAssign
                    severity={selected.severity}
                    onAssign={(severity) =>
                      safeCall(
                        () => assignHazardTicket(selected.id, { owner_id: ownerId, severity }),
                        "已派单给维保人员"
                      )
                    }
                  />
                ) : null}

                {isMaintainer &&
                selected.rectify_status === "ASSIGNED" &&
                selected.owner_id === user?.id ? (
                  <div className="action-form">
                    <textarea
                      placeholder="填写整改措施、更换部件与自检结果"
                      value={rectifyNote}
                      onChange={(e) => setRectifyNote(e.target.value)}
                    />
                    <button
                      className="btn btn-primary"
                      disabled={!rectifyNote.trim()}
                      onClick={() =>
                        safeCall(
                          () => rectifyHazardTicket(selected.id, rectifyNote),
                          "整改结果已提交，等待主管复验"
                        ).then(() => setRectifyNote(""))
                      }
                    >
                      提交整改
                    </button>
                  </div>
                ) : null}

                {isSupervisor && selected.rectify_status === "RECTIFIED" ? (
                  <div className="action-form">
                    <textarea
                      placeholder="复验结论（可选）"
                      value={reviewNote}
                      onChange={(e) => setReviewNote(e.target.value)}
                    />
                    <div className="action-group">
                      <button
                        className="btn btn-primary"
                        onClick={() =>
                          safeCall(
                            () =>
                              closeHazardTicket(selected.id, {
                                note: reviewNote,
                                pass_review: true
                              }),
                            "复验通过，隐患已关闭，设备状态已重新计算"
                          ).then(() => setReviewNote(""))
                        }
                      >
                        复验通过关闭
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() =>
                          safeCall(
                            () =>
                              closeHazardTicket(selected.id, {
                                note: reviewNote || "复验不通过",
                                pass_review: false
                              }),
                            "已退回维保人员重新整改"
                          ).then(() => setReviewNote(""))
                        }
                      >
                        不通过退回
                      </button>
                    </div>
                  </div>
                ) : null}

                {selected.rectify_status === "CLOSED" ? (
                  <p className="form-notice">该隐患单已于 {formatDate(selected.closed_at)} 复验关闭</p>
                ) : null}
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function SupervisorAssign({
  severity,
  onAssign
}: {
  severity: string;
  onAssign: (severity: string) => void;
}) {
  const [value, setValue] = useState(severity);
  return (
    <div className="action-form">
      <label>
        隐患级别
        <select value={value} onChange={(e) => setValue(e.target.value)}>
          {HazardSeverity.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </label>
      <button className="btn btn-primary" onClick={() => onAssign(value)}>
        派单给维保-老周
      </button>
    </div>
  );
}
