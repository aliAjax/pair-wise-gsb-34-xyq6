import { request } from "./client";
import type { InspectionTask } from "../types/InspectionTask";

export interface TaskQuery {
  buildingId?: number;
  status?: string;
}

export async function listInspectionTask(query: TaskQuery = {}): Promise<InspectionTask[]> {
  const params = new URLSearchParams();
  if (query.buildingId) params.set("building_id", String(query.buildingId));
  if (query.status) params.set("status", query.status);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return request<InspectionTask[]>(`/inspection-task${suffix}`);
}

export async function getInspectionTask(taskId: number): Promise<InspectionTask> {
  return request<InspectionTask>(`/inspection-task/${taskId}`);
}

export async function createInspectionTask(
  payload: { building_id: number; task_type: string; plan_date?: string }
): Promise<InspectionTask> {
  return request<InspectionTask>("/inspection-task", { method: "POST", body: payload });
}

export async function claimInspectionTask(taskId: number): Promise<InspectionTask> {
  return request<InspectionTask>(`/inspection-task/${taskId}/claim`, { method: "POST" });
}

export async function submitInspectionTask(taskId: number): Promise<InspectionTask> {
  return request<InspectionTask>(`/inspection-task/${taskId}/submit`, { method: "POST" });
}

export async function reviewInspectionTask(
  taskId: number,
  note: string
): Promise<InspectionTask> {
  return request<InspectionTask>(`/inspection-task/${taskId}/review`, {
    method: "POST",
    body: { note }
  });
}

export async function bumpChecklistVersion(taskId: number): Promise<InspectionTask> {
  return request<InspectionTask>(`/inspection-task/${taskId}/checklist-version`, {
    method: "POST"
  });
}
