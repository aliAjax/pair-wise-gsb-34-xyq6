export interface Building {
  id: number;
  name: string;
  campus: string;
  floor_count: number;
  fire_grade: string;
  manager_id: number | null;
  address_code: string;
  manager_name?: string;
  device_count?: number;
  task_count?: number;
}
