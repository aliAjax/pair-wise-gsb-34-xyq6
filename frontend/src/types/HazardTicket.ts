export interface HazardTicket {
  id: number;
  result_id: number;
  task_id: number;
  device_id: number;
  device_code: string;
  building_name: string;
  item_code: string;
  item_name: string;
  result_note: string;
  severity: string;
  owner_id: number | null;
  owner_name: string;
  deadline: string | null;
  rectify_status: string;
  rectify_note: string;
  created_at: string | null;
  rectified_at: string | null;
  closed_at: string | null;
  closed_by: number | null;
  overdue: boolean;
}
