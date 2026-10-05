import { request } from "./client";
import type { AuditLog } from "../types/AuditLog";

export function listAuditLogs(limit = 100): Promise<AuditLog[]> {
  return request<AuditLog[]>("/audit-log", { query: { limit } });
}
