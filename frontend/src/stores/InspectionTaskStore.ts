import { create } from "zustand";
import { listInspectionTask, type TaskQuery } from "../api/InspectionTask";
import type { InspectionTask } from "../types/InspectionTask";

interface InspectionTaskState {
  rows: InspectionTask[];
  loading: boolean;
  error: string;
  load: (query?: TaskQuery) => Promise<void>;
}

export const useInspectionTaskStore = create<InspectionTaskState>((set) => ({
  rows: [],
  loading: false,
  error: "",
  async load(query) {
    set({ loading: true, error: "" });
    try {
      set({ rows: await listInspectionTask(query), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  }
}));
