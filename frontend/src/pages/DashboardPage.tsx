import { useEffect } from "react";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { useHazardTicketStore } from "../stores/HazardTicketStore";
import { useInspectionTaskStore } from "../stores/InspectionTaskStore";
import { useStatsStore } from "../stores/StatsStore";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { EmptyState } from "../components/common/EmptyState";
import { formatDate, formatDeviceStatus, formatPercent } from "../utils/formatters";
import { useHazardFlow } from "../hooks/useHazardFlow";
import { useAuthStore } from "../stores/AuthStore";

export function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const stats = useStatsStore((state) => state.dashboard);
  const loadDashboard = useStatsStore((state) => state.loadDashboard);
  const devices = useFireDeviceStore((state) => state.rows);
  const loadDevices = useFireDeviceStore((state) => state.load);
  const tasks = useInspectionTaskStore((state) => state.rows);
  const loadTasks = useInspectionTaskStore((state) => state.load);
  const hazards = useHazardTicketStore((state) => state.rows);
  const loadHazards = useHazardTicketStore((state) => state.load);

  useEffect(() => {
    void loadDashboard();
    void loadDevices();
    void loadTasks();
    void loadHazards();
  }, [loadDashboard, loadDevices, loadTasks, loadHazards]);

  const flow = useHazardFlow(hazards);
  const openHazards = hazards
    .filter((h) => h.rectify_status !== "CLOSED")
    .sort((a, b) => Number(b.overdue) - Number(a.overdue))
    .slice(0, 6);
  const recentTasks = tasks.slice(0, 5);

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>消防合规总览</h1>
        </div>
        <StatusBadge value="LIVE" label="实时数据" />
      </section>

      <section className="metrics">
        <StatCard
          label="消防设备总数"
          value={stats?.device_total ?? "—"}
          hint={`正常 ${stats?.device_normal ?? 0} · 故障 ${stats?.device_fault ?? 0}`}
        />
        <StatCard
          label="整改中设备"
          value={stats?.device_maintaining ?? "—"}
          tone="warn"
          hint={`未结隐患 ${stats?.open_hazard_total ?? 0} 张`}
        />
        <StatCard
          label="逾期隐患"
          value={stats?.overdue_hazard_total ?? "—"}
          tone="danger"
          hint={`严重隐患 ${stats?.critical_hazard_total ?? 0} 张`}
        />
        <StatCard
          label="巡检完成率"
          value={stats ? formatPercent(stats.inspection_completion_rate) : "—"}
          hint={`${stats?.task_finished ?? 0}/${stats?.task_total ?? 0} 个任务`}
        />
        <StatCard
          label="隐患整改率"
          value={stats ? formatPercent(stats.rectification_rate) : "—"}
          tone="ok"
        />
      </section>

      <section className="workbench">
        <div className="panel wide">
          <h2>高危与逾期隐患</h2>
          {openHazards.length === 0 ? (
            <EmptyState title="当前没有未结隐患" hint="巡检异常会自动在此生成隐患单" />
          ) : (
            <div className="table">
              {openHazards.map((hazard) => (
                <article className="row" key={hazard.id}>
                  <div>
                    <strong>{hazard.building_name} · {hazard.device_code}</strong>
                    <span className="muted">{hazard.item_name}（{hazard.item_code}）</span>
                  </div>
                  <HazardSeverityTag value={hazard.severity} />
                  <StatusBadge value={hazard.rectify_status} label={undefined} />
                  <span className={hazard.overdue ? "text-danger" : "muted"}>
                    期限 {formatDate(hazard.deadline)}
                    {hazard.overdue ? " · 已逾期" : ""}
                  </span>
                </article>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <h2>隐患流转</h2>
          <ul className="flow-stages">
            {flow.stages.map((stage) => (
              <li key={stage.key}>
                <span>{stage.label}</span>
                <strong>{stage.count}</strong>
              </li>
            ))}
            <li className="danger">
              <span>逾期</span>
              <strong>{flow.overdueCount}</strong>
            </li>
          </ul>
          <h2>设备状态分布</h2>
          <ul className="flow-stages">
            <li><span>{formatDeviceStatus("NORMAL")}</span><strong>{stats?.device_normal ?? 0}</strong></li>
            <li><span>{formatDeviceStatus("FAULT")}</span><strong>{stats?.device_fault ?? 0}</strong></li>
            <li><span>{formatDeviceStatus("MAINTAINING")}</span><strong>{stats?.device_maintaining ?? 0}</strong></li>
            <li><span>{formatDeviceStatus("SCRAPPED")}</span><strong>{stats?.device_scrapped ?? 0}</strong></li>
          </ul>
        </div>
      </section>

      <section className="panel">
        <h2>最近巡检任务</h2>
        <div className="table">
          {recentTasks.map((task) => (
            <article className="row" key={task.id}>
              <div>
                <strong>#{task.id} {task.building_name}</strong>
                <span className="muted">
                  {task.task_type} · 检查项 {task.submitted_items}/{task.total_items}
                </span>
              </div>
              <StatusBadge value={task.status} />
              <span className="muted">计划 {formatDate(task.plan_date)}</span>
            </article>
          ))}
        </div>
        <p className="muted">当前登录：{user?.name}（{user ? user.role : ""}）</p>
      </section>
    </main>
  );
}
