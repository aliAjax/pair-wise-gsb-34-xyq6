import { create } from "zustand";
import { listInspectionTask } from "../api/InspectionTask";
import type { InspectionTask } from "../types/InspectionTask";

type State = {
  rows: InspectionTask[];
  loading: boolean;
  error: string | null;
  load: (params?: { building_id?: number; status?: string }) => Promise<void>;
};

export const useInspectionTaskStore = create<State>((set) => ({
  rows: [],
  loading: false,
  error: null,
  async load(params) {
    set({ loading: true, error: null });
    try {
      set({ rows: await listInspectionTask(params), loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },
}));
