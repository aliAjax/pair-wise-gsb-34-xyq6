export interface FireDevice {
  id: number;
  building_id: number;
  building_name: string;
  device_code: string;
  device_type: string;
  floor: string;
  location_desc: string;
  install_date: string | null;
  status: string;
  next_maintenance_at: string | null;
  open_hazard_count: number;
}
