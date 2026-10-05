import { create } from "zustand";
import { getDashboard, getMonthlyReport, listAuditLogs } from "../api/Stats";
import type { AuditLogEntry, DashboardStats, MonthlyReportRow } from "../types/Stats";

interface StatsState {
  dashboard: DashboardStats | null;
  report: MonthlyReportRow[];
  logs: AuditLogEntry[];
  loading: boolean;
  error: string;
  loadDashboard: () => Promise<void>;
  loadReport: () => Promise<void>;
  loadLogs: () => Promise<void>;
}

export const useStatsStore = create<StatsState>((set) => ({
  dashboard: null,
  report: [],
  logs: [],
  loading: false,
  error: "",
  async loadDashboard() {
    set({ loading: true, error: "" });
    try {
      set({ dashboard: await getDashboard(), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  },
  async loadReport() {
    set({ loading: true, error: "" });
    try {
      set({ report: await getMonthlyReport(), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  },
  async loadLogs() {
    set({ loading: true, error: "" });
    try {
      set({ logs: await listAuditLogs(), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  }
}));
