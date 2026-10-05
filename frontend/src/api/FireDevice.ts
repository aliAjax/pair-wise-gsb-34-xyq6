import { request } from "./client";
import type { FireDevice } from "../types/FireDevice";

export function listFireDevice(buildingId?: number): Promise<FireDevice[]> {
  return request<FireDevice[]>("/fire-device", { query: { building_id: buildingId } });
}

export function createFireDevice(payload: {
  building_id: number;
  device_code: string;
  device_type: string;
  floor: string;
  location_desc: string;
  install_date?: string;
  next_maintenance_at?: string;
}): Promise<FireDevice> {
  return request<FireDevice>("/fire-device", { method: "POST", body: payload });
}
