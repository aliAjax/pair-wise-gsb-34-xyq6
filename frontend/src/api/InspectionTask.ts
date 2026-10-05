import { request } from "./client";
import type { InspectionTask, ChecklistDetail } from "../types/InspectionTask";

export function listInspectionTask(params?: {
  building_id?: number;
  status?: string;
}): Promise<InspectionTask[]> {
  return request<InspectionTask[]>("/inspection-task", { query: params });
}

export function createInspectionTask(payload: {
  building_id: number;
  plan_date: string;
  task_type: string;
}): Promise<InspectionTask> {
  return request<InspectionTask>("/inspection-task", { method: "POST", body: payload });
}

export function claimInspectionTask(taskId: number): Promise<InspectionTask> {
  return request<InspectionTask>(`/inspection-task/${taskId}/claim`, { method: "POST" });
}

export function getTaskChecklist(taskId: number): Promise<ChecklistDetail> {
  return request<ChecklistDetail>(`/inspection-task/${taskId}/checklist`);
}

export function reviewInspectionTask(taskId: number, approved: boolean): Promise<InspectionTask> {
  return request<InspectionTask>(`/inspection-task/${taskId}/review`, {
    method: "POST",
    body: { approved },
  });
}

export function publishChecklist(payload: {
  task_type: string;
  items: { item_code: string; item_name: string }[];
}): Promise<{ task_type: string; checklist_version: string; superseded_tasks: number[] }> {
  return request("/inspection-task/checklist/publish", { method: "POST", body: payload });
}
