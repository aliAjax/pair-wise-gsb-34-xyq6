import { useEffect, useState } from "react";
import { listAuditLogs } from "../api/AuditLog";
import { fetchMonthlyReport, fetchOverview } from "../api/Dashboard";
import { AlertBanner } from "../components/common/AlertBanner";
import { EmptyState } from "../components/common/EmptyState";
import { PageHeader } from "../components/common/PageHeader";
import { StatCard } from "../components/common/StatCard";
import { TimelineList, auditLogToTimeline } from "../components/common/TimelineList";
import type { AuditLog } from "../types/AuditLog";
import type { DashboardOverview, MonthlyReportRow } from "../types/Dashboard";
import { formatPercent } from "../utils/formatters";

export function ReportsPage() {
  const [report, setReport] = useState<MonthlyReportRow[]>([]);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchMonthlyReport(), fetchOverview(), listAuditLogs(200)])
      .then(([reportRes, overviewRes, logRows]) => {
        setReport(reportRes.months);
        setOverview(overviewRes);
        setLogs(logRows);
      })
      .catch((err) => setError(err.message));
  }, []);

  const maxFault = Math.max(1, ...report.map((row) => row.abnormal_result_count));

  return (
    <main className="page">
      <PageHeader title="合规报表 / 审计台账" eyebrow="月度巡检率、整改率、故障率与操作审计" />
      {error && <AlertBanner tone="danger" onClose={() => setError(null)}>{error}</AlertBanner>}

      <section className="metrics">
        <StatCard label="设备总数" value={overview?.device_total ?? "—"} />
        <StatCard label="巡检完成率" value={overview ? formatPercent(overview.task_completion_rate) : "—"} tone="ok" />
        <StatCard label="未闭环隐患" value={overview?.open_ticket_count ?? "—"} tone={overview && overview.open_ticket_count > 0 ? "danger" : "ok"} />
        <StatCard label="严重隐患" value={overview?.critical_ticket_count ?? "—"} tone={overview && overview.critical_ticket_count > 0 ? "danger" : "default"} />
      </section>

      <section className="panel">
        <h2>月度统计</h2>
        {report.length === 0 ? (
          <EmptyState title="暂无月度数据" hint="完成巡检与隐患闭环后自动生成" />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>月份</th>
                <th>巡检任务</th>
                <th>合格/异常项</th>
                <th>设备故障率</th>
                <th>开单/关闭</th>
                <th>整改率</th>
                <th>故障项趋势</th>
              </tr>
            </thead>
            <tbody>
              {report.map((row) => (
                <tr key={row.month}>
                  <td><strong>{row.month}</strong></td>
                  <td>{row.task_count}</td>
                  <td>
                    <span className="ok-text">{row.normal_result_count}</span>
                    {" / "}
                    <span className="danger-text">{row.abnormal_result_count}</span>
                  </td>
                  <td>{formatPercent(row.device_fault_rate)}</td>
                  <td>{row.ticket_created} / {row.ticket_closed}</td>
                  <td>{formatPercent(row.rectify_rate)}</td>
                  <td>
                    <div className="mini-bar">
                      <div className="mini-bar-fill" style={{ width: `${(row.abnormal_result_count / maxFault) * 100}%` }} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="panel">
        <h2>操作审计日志（巡检提交 / 隐患派单 / 复验关闭等写操作）</h2>
        {logs.length === 0 ? (
          <EmptyState title="暂无审计日志" />
        ) : (
          <TimelineList items={logs.map(auditLogToTimeline)} />
        )}
      </section>
    </main>
  );
}
