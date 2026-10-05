import { request } from "./client";
import type { FireDevice } from "../types/FireDevice";

export async function listFireDevice(buildingId?: number): Promise<FireDevice[]> {
  const query = buildingId ? `?building_id=${buildingId}` : "";
  return request<FireDevice[]>(`/fire-device${query}`);
}

export interface FireDeviceForm {
  building_id: number;
  device_code: string;
  device_type: string;
  floor: string;
  location_desc: string;
  install_date?: string | null;
  next_maintenance_at?: string | null;
}

export async function createFireDevice(payload: FireDeviceForm): Promise<FireDevice> {
  return request<FireDevice>("/fire-device", { method: "POST", body: payload });
}
