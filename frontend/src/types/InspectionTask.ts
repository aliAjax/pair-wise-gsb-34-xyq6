export interface InspectionTask {
  id: number;
  building_id: number;
  inspector_id: number | null;
  plan_date: string;
  task_type: string;
  status: string;
  checklist_version: string;
  finished_at: string | null;
}

export interface ChecklistItem {
  item_code: string;
  item_name: string;
  checklist_version: string;
  deprecated: boolean;
  filled: boolean;
  result_status: string | null;
}

export interface ChecklistDetail {
  task: InspectionTask;
  current_version: string;
  items: ChecklistItem[];
}

export interface SubmitResultItem {
  device_id: number;
  item_code: string;
  result_status: string;
  measured_value?: string | null;
  photo_url?: string | null;
  note?: string | null;
}

export interface SubmitResultResponse {
  task_id: number;
  task_status: string;
  checklist_version: string;
  current_version: string;
  stale: boolean;
  saved: { item_code: string; device_id: number; result_status: string }[];
  rejected: { item_code: string; device_id: number | null; reason_code: string; reason: string }[];
  all_items_completed: boolean;
}
