export interface InspectionResult {
  id: number;
  task_id: number;
  device_id: number;
  item_name: string;
  item_code: string;
  result_status: "NORMAL" | "ABNORMAL";
  measured_value: string;
  photo_url: string;
  note: string;
  submitted_by: number | null;
  submitted_by_name: string;
  submitted_at: string | null;
  device_code: string;
  building_name: string;
  hazard_id: number | null;
}

export interface SubmitResultItem {
  item_code: string;
  checklist_version: number;
  result_status: "NORMAL" | "ABNORMAL";
  measured_value?: string;
  photo_url?: string;
  note?: string;
  severity?: string;
}

export interface SubmittedResult {
  item_code: string;
  result_id: number;
  result_status: "NORMAL" | "ABNORMAL";
  hazard_id: number | null;
}

export interface ResultConflict {
  item_code: string;
  code: string;
  message: string;
}

export interface SubmitBatchResponse {
  task_id: number;
  saved: SubmittedResult[];
  conflicts: ResultConflict[];
  task: import("./InspectionTask").InspectionTask;
}
