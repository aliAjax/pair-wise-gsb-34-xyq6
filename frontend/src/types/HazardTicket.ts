export interface HazardTicket {
  id: number;
  result_id: number;
  device_id: number;
  severity: string;
  owner_id: number | null;
  deadline: string | null;
  rectify_status: string;
  rectify_note: string | null;
  closed_at: string | null;
}
