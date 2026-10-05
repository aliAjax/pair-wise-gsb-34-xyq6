import { request } from "./client";
import type { Building } from "../types/Building";

export async function listBuilding(): Promise<Building[]> {
  return request<Building[]>("/building");
}

export interface BuildingForm {
  name: string;
  campus: string;
  floor_count: number;
  fire_grade: string;
  manager_id?: number | null;
  address_code: string;
}

export async function createBuilding(payload: BuildingForm): Promise<Building> {
  return request<Building>("/building", { method: "POST", body: payload });
}
