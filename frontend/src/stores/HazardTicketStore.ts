import { create } from "zustand";
import { listHazardTicket } from "../api/HazardTicket";
import type { HazardTicket } from "../types/HazardTicket";

type State = {
  rows: HazardTicket[];
  loading: boolean;
  error: string | null;
  load: (params?: { rectify_status?: string; device_id?: number }) => Promise<void>;
};

export const useHazardTicketStore = create<State>((set) => ({
  rows: [],
  loading: false,
  error: null,
  async load(params) {
    set({ loading: true, error: null });
    try {
      set({ rows: await listHazardTicket(params), loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },
}));
