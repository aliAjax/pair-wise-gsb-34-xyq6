import type { HazardTicket } from "../types/HazardTicket";

export const createDefaultHazardTicket = (
  overrides: Partial<HazardTicket> = {}
): HazardTicket => ({
  id: 0,
  result_id: 0,
  task_id: 0,
  device_id: 0,
  device_code: "",
  building_name: "",
  item_code: "",
  item_name: "",
  result_note: "",
  severity: "MEDIUM",
  owner_id: null,
  owner_name: "",
  deadline: null,
  rectify_status: "OPEN",
  rectify_note: "",
  created_at: null,
  rectified_at: null,
  closed_at: null,
  closed_by: null,
  overdue: false,
  ...overrides
});

export const createHazardTicketForm = (overrides: Partial<HazardTicket> = {}) =>
  createDefaultHazardTicket(overrides);
export const createHazardTicketResponse = createDefaultHazardTicket;
