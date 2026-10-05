import { request } from "./client";
import type { AuditLogEntry, DashboardStats, MonthlyReportRow } from "../types/Stats";

export async function getDashboard(): Promise<DashboardStats> {
  return request<DashboardStats>("/stats/dashboard");
}

export async function getMonthlyReport(): Promise<MonthlyReportRow[]> {
  return request<MonthlyReportRow[]>("/stats/monthly-report");
}

export async function listAuditLogs(): Promise<AuditLogEntry[]> {
  return request<AuditLogEntry[]>("/auth/audit-logs");
}
