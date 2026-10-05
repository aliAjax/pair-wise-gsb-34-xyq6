import { create } from "zustand";
import { listBuilding } from "../api/Building";
import type { Building } from "../types/Building";

interface BuildingState {
  rows: Building[];
  loading: boolean;
  error: string;
  load: () => Promise<void>;
}

export const useBuildingStore = create<BuildingState>((set) => ({
  rows: [],
  loading: false,
  error: "",
  async load() {
    set({ loading: true, error: "" });
    try {
      set({ rows: await listBuilding(), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  }
}));
