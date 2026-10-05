import { create } from "zustand";
import { listHazardTicket, type HazardQuery } from "../api/HazardTicket";
import type { HazardTicket } from "../types/HazardTicket";

interface HazardTicketState {
  rows: HazardTicket[];
  loading: boolean;
  error: string;
  load: (query?: HazardQuery) => Promise<void>;
}

export const useHazardTicketStore = create<HazardTicketState>((set) => ({
  rows: [],
  loading: false,
  error: "",
  async load(query) {
    set({ loading: true, error: "" });
    try {
      set({ rows: await listHazardTicket(query), loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  }
}));
