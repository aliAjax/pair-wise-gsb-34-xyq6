import { request } from "./client";
import type {
  InspectionResult,
  SubmitBatchResponse,
  SubmitResultItem
} from "../types/InspectionResult";

export async function listInspectionResult(
  params: { taskId?: number; deviceId?: number } = {}
): Promise<InspectionResult[]> {
  const query = new URLSearchParams();
  if (params.taskId) query.set("task_id", String(params.taskId));
  if (params.deviceId) query.set("device_id", String(params.deviceId));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request<InspectionResult[]>(`/inspection-result${suffix}`);
}

export async function submitInspectionResults(
  taskId: number,
  items: SubmitResultItem[]
): Promise<SubmitBatchResponse> {
  return request<SubmitBatchResponse>(`/inspection-result/task/${taskId}/submit`, {
    method: "POST",
    body: { items }
  });
}
