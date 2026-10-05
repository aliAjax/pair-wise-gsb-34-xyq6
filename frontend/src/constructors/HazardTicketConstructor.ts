import type { HazardTicket } from "../types/HazardTicket";

export const createDefaultHazardTicket = (overrides: Partial<HazardTicket> = {}): HazardTicket => ({
  id: 0,
  result_id: 0,
  device_id: 0,
  severity: "MEDIUM",
  owner_id: null,
  deadline: null,
  rectify_status: "OPEN",
  rectify_note: null,
  closed_at: null,
  ...overrides,
});

export const createHazardTicketForm = createDefaultHazardTicket;
export const createHazardTicketResponse = createDefaultHazardTicket;
