export interface DashboardStats {
  device_total: number;
  device_normal: number;
  device_fault: number;
  device_maintaining: number;
  device_scrapped: number;
  open_hazard_total: number;
  overdue_hazard_total: number;
  critical_hazard_total: number;
  task_total: number;
  task_finished: number;
  inspection_completion_rate: number;
  rectification_rate: number;
}

export interface MonthlyReportRow {
  month: string;
  task_total: number;
  task_finished: number;
  inspection_rate: number;
  hazard_total: number;
  hazard_closed: number;
  rectification_rate: number;
  abnormal_device_count: number;
}

export interface AuditLogEntry {
  id: number;
  actor_id: number | null;
  actor_name: string;
  actor_role: string;
  action: string;
  action_label: string;
  target_type: string;
  target_id: string;
  detail: string;
  created_at: string | null;
}
