export interface ChecklistItem {
  id: number;
  device_id: number;
  item_code: string;
  item_name: string;
  checklist_version: number;
  result_status: "NORMAL" | "ABNORMAL" | null;
  measured_value: string;
  photo_url: string;
  note: string;
  submitted_by: number | null;
  submitted_by_name: string;
  submitted_at: string | null;
  hazard_id: number | null;
  hazard_status: string | null;
}

export interface InspectionTask {
  id: number;
  building_id: number;
  building_name: string;
  inspector_id: number | null;
  inspector_name: string;
  plan_date: string;
  task_type: string;
  status: string;
  checklist_version: number;
  finished_at: string | null;
  reviewed_at: string | null;
  created_at: string;
  total_items: number;
  submitted_items: number;
  abnormal_items: number;
  open_hazard_count: number;
  items: ChecklistItem[];
}
