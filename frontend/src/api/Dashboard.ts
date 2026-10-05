import { request } from "./client";
import type { DashboardOverview, MonthlyReportRow } from "../types/Dashboard";

export function fetchOverview(): Promise<DashboardOverview> {
  return request<DashboardOverview>("/dashboard/overview");
}

export function fetchMonthlyReport(): Promise<{ months: MonthlyReportRow[] }> {
  return request<{ months: MonthlyReportRow[] }>("/dashboard/monthly-report");
}
