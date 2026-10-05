import { useEffect, useState } from "react";
import { EmptyState } from "../components/common/EmptyState";
import { StatCard } from "../components/common/StatCard";
import { useAuthStore } from "../stores/AuthStore";
import { useStatsStore } from "../stores/StatsStore";
import { formatDate, formatPercent } from "../utils/formatters";

export function ReportsPage() {
  const user = useAuthStore((state) => state.user);
  const report = useStatsStore((state) => state.report);
  const logs = useStatsStore((state) => state.logs);
  const loading = useStatsStore((state) => state.loading);
  const loadReport = useStatsStore((state) => state.loadReport);
  const loadLogs = useStatsStore((state) => state.loadLogs);

  const [tab, setTab] = useState<"report" | "audit">("report");

  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  useEffect(() => {
    if (tab === "audit") void loadLogs();
  }, [tab, loadLogs]);

  const finishedTotal = report.reduce((sum, r) => sum + r.task_finished, 0);
  const taskTotal = report.reduce((sum, r) => sum + r.task_total, 0);
  const closedTotal = report.reduce((sum, r) => sum + r.hazard_closed, 0);
  const hazardTotal = report.reduce((sum, r) => sum + r.hazard_total, 0);

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>合规报表</h1>
        </div>
        <div className="tabs">
          <button className={tab === "report" ? "active" : ""} onClick={() => setTab("report")}>
            月度统计
          </button>
          {user?.role === "AUDITOR" || user?.role === "SUPERVISOR" ? (
            <button className={tab === "audit" ? "active" : ""} onClick={() => setTab("audit")}>
              操作审计日志
            </button>
          ) : null}
        </div>
      </section>

      {tab === "report" ? (
        <>
          <section className="metrics">
            <StatCard label="累计巡检任务" value={taskTotal} hint={`已完成 ${finishedTotal}`} />
            <StatCard
              label="累计巡检完成率"
              value={taskTotal ? formatPercent(finishedTotal / taskTotal) : "—"}
            />
            <StatCard label="累计隐患单" value={hazardTotal} hint={`已关闭 ${closedTotal}`} />
            <StatCard
              label="累计整改率"
              value={hazardTotal ? formatPercent(closedTotal / hazardTotal) : "—"}
              tone="ok"
            />
          </section>

          <section className="panel">
            <h2>月度巡检率 / 整改率 {loading ? "加载中…" : ""}</h2>
            {report.length === 0 ? (
              <EmptyState title="暂无报表数据" />
            ) : (
              <div className="report-table">
                <div className="report-row report-head">
                  <span>月份</span>
                  <span>巡检任务</span>
                  <span>巡检率</span>
                  <span>隐患单</span>
                  <span>整改率</span>
                  <span>异常设备</span>
                </div>
                {report.map((row) => (
                  <div className="report-row" key={row.month}>
                    <span>{row.month}</span>
                    <span>{row.task_finished}/{row.task_total}</span>
                    <RateCell value={row.inspection_rate} />
                    <span>{row.hazard_closed}/{row.hazard_total}</span>
                    <RateCell value={row.rectification_rate} />
                    <span>{row.abnormal_device_count}</span>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      ) : (
        <section className="panel">
          <h2>操作审计日志（最近 200 条）</h2>
          {logs.length === 0 ? (
            <EmptyState title="暂无审计日志" />
          ) : (
            <ul className="audit-list">
              {logs.map((log) => (
                <li key={log.id}>
                  <time>{formatDate(log.created_at)}</time>
                  <div>
                    <strong>{log.action_label}</strong>
                    <span className="muted">
                      {log.actor_name || log.actor_role} · {log.target_type}#{log.target_id}
                    </span>
                    <p>{log.detail}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </main>
  );
}

function RateCell({ value }: { value: number }) {
  return (
    <span className={value >= 0.8 ? "text-ok" : value >= 0.5 ? "text-warn" : "text-danger"}>
      {formatPercent(value)}
    </span>
  );
}
