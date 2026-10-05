import { create } from "zustand";
import { listBuilding } from "../api/Building";
import type { Building } from "../types/Building";

type State = {
  rows: Building[];
  loading: boolean;
  error: string | null;
  load: () => Promise<void>;
};

export const useBuildingStore = create<State>((set) => ({
  rows: [],
  loading: false,
  error: null,
  async load() {
    set({ loading: true, error: null });
    try {
      set({ rows: await listBuilding(), loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },
}));
