import { useEffect, useState } from "react";
import { fetchOverview } from "../api/Dashboard";
import { AlertBanner } from "../components/common/AlertBanner";
import { PageHeader } from "../components/common/PageHeader";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceStatusLabels } from "../constants/DeviceStatus";
import { RectifyStatusLabels } from "../constants/RectifyStatus";
import type { DashboardOverview } from "../types/Dashboard";
import { formatPercent } from "../utils/formatters";

const DEVICE_ORDER = ["NORMAL", "MAINTAINING", "FAULT", "SCRAPPED"];
const TICKET_ORDER = ["OPEN", "ASSIGNED", "RECTIFIED", "REJECTED", "CLOSED"];

export function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    fetchOverview().then(setOverview).catch((err) => setError(err.message));
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <main className="page">
      <PageHeader title="消防合规总览" actions={<button className="btn" onClick={load}>刷新数据</button>} />
      {error && <AlertBanner tone="danger" onClose={() => setError(null)}>{error}</AlertBanner>}

      <section className="metrics">
        <StatCard label="消防设备总数" value={overview?.device_total ?? "—"} hint="全园区在册设备" />
        <StatCard
          label="巡检完成率"
          value={overview ? formatPercent(overview.task_completion_rate) : "—"}
          hint={`共 ${overview?.task_total ?? 0} 个巡检任务`}
        />
        <StatCard
          label="未闭环隐患"
          value={overview?.open_ticket_count ?? "—"}
          tone={overview && overview.open_ticket_count > 0 ? "danger" : "ok"}
          hint={`逾期未整改 ${overview?.overdue_ticket_count ?? 0} 单`}
        />
        <StatCard
          label="严重隐患"
          value={overview?.critical_ticket_count ?? "—"}
          tone={overview && overview.critical_ticket_count > 0 ? "danger" : "default"}
        />
        <StatCard
          label="逾期未领取任务"
          value={overview?.overdue_task_count ?? "—"}
          tone={overview && overview.overdue_task_count > 0 ? "warn" : "default"}
        />
      </section>

      <section className="workbench dashboard-grid">
        <div className="panel">
          <h2>设备状态分布（实时重算）</h2>
          <div className="dist-list">
            {DEVICE_ORDER.map((status) => (
              <div className="dist-row" key={status}>
                <StatusBadge value={status} label={DeviceStatusLabels[status as keyof typeof DeviceStatusLabels] ?? status} />
                <span className="dist-count">{overview?.device_status_distribution[status] ?? 0}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <h2>隐患整改分布</h2>
          <div className="dist-list">
            {TICKET_ORDER.map((status) => (
              <div className="dist-row" key={status}>
                <StatusBadge value={status} label={RectifyStatusLabels[status as keyof typeof RectifyStatusLabels]} />
                <span className="dist-count">{overview?.ticket_status_distribution[status] ?? 0}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
