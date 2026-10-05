export interface DashboardOverview {
  device_total: number;
  device_status_distribution: Record<string, number>;
  ticket_status_distribution: Record<string, number>;
  open_ticket_count: number;
  overdue_ticket_count: number;
  overdue_task_count: number;
  task_total: number;
  task_completion_rate: number;
  critical_ticket_count: number;
}

export interface MonthlyReportRow {
  month: string;
  task_count: number;
  normal_result_count: number;
  abnormal_result_count: number;
  ticket_created: number;
  ticket_closed: number;
  rectify_rate: number;
  device_fault_rate: number;
}
