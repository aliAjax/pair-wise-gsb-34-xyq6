import { create } from "zustand";
import { listFireDevice } from "../api/FireDevice";
import type { FireDevice } from "../types/FireDevice";

interface FireDeviceState {
  rows: FireDevice[];
  loading: boolean;
  error: string;
  load: (buildingId?: number) => Promise<void>;
}

export const useFireDeviceStore = create<FireDeviceState>((set) => ({
  rows: [],
  loading: false,
  error: "",
  async load(buildingId) {
    set({ loading: true, error: "" });
    try {
      set({ rows: await listFireDevice(buildingId), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  }
}));
