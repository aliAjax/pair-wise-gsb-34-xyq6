import { request } from "./client";
import type { InspectionResult } from "../types/InspectionResult";
import type { SubmitResultItem, SubmitResultResponse } from "../types/InspectionTask";

export function listInspectionResult(params?: {
  task_id?: number;
  device_id?: number;
}): Promise<InspectionResult[]> {
  return request<InspectionResult[]>("/inspection-result", { query: params });
}

export function submitInspectionResults(
  taskId: number,
  checklistVersion: string,
  items: SubmitResultItem[],
): Promise<SubmitResultResponse> {
  return request<SubmitResultResponse>(`/inspection-result/task/${taskId}/submit`, {
    method: "POST",
    body: { checklist_version: checklistVersion, items },
  });
}
