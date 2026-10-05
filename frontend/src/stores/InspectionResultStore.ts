import { create } from "zustand";
import { listInspectionResult } from "../api/InspectionResult";
import type { InspectionResult } from "../types/InspectionResult";

interface InspectionResultState {
  rows: InspectionResult[];
  loading: boolean;
  error: string;
  load: (params?: { taskId?: number; deviceId?: number }) => Promise<void>;
}

export const useInspectionResultStore = create<InspectionResultState>((set) => ({
  rows: [],
  loading: false,
  error: "",
  async load(params) {
    set({ loading: true, error: "" });
    try {
      set({ rows: await listInspectionResult(params), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  }
}));
