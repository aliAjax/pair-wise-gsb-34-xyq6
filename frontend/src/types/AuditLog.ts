export interface AuditLog {
  id: number;
  actor: string;
  action: string;
  target_type: string;
  target_id: string;
  detail: string | null;
  created_at: string | null;
}
