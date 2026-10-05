import { create } from "zustand";
import { listFireDevice } from "../api/FireDevice";
import type { FireDevice } from "../types/FireDevice";

type State = {
  rows: FireDevice[];
  loading: boolean;
  error: string | null;
  load: (buildingId?: number) => Promise<void>;
};

export const useFireDeviceStore = create<State>((set) => ({
  rows: [],
  loading: false,
  error: null,
  async load(buildingId) {
    set({ loading: true, error: null });
    try {
      set({ rows: await listFireDevice(buildingId), loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },
}));
