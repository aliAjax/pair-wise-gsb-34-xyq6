export interface InspectionResult {
  id: number;
  task_id: number;
  device_id: number;
  item_code: string;
  result_status: string;
  measured_value: string | null;
  photo_url: string | null;
  note: string | null;
  checklist_version: string;
}
