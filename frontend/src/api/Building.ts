import { request } from "./client";
import type { Building } from "../types/Building";

export function listBuilding(): Promise<Building[]> {
  return request<Building[]>("/building");
}
