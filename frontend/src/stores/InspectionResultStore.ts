import { create } from "zustand";
import { listInspectionResult } from "../api/InspectionResult";
import type { InspectionResult } from "../types/InspectionResult";

type State = {
  rows: InspectionResult[];
  loading: boolean;
  error: string | null;
  load: (params?: { task_id?: number; device_id?: number }) => Promise<void>;
};

export const useInspectionResultStore = create<State>((set) => ({
  rows: [],
  loading: false,
  error: null,
  async load(params) {
    set({ loading: true, error: null });
    try {
      set({ rows: await listInspectionResult(params), loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },
}));
