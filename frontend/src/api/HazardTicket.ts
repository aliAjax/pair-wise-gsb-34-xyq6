import { request } from "./client";
import type { HazardTicket } from "../types/HazardTicket";

export function listHazardTicket(params?: {
  rectify_status?: string;
  device_id?: number;
}): Promise<HazardTicket[]> {
  return request<HazardTicket[]>("/hazard-ticket", { query: params });
}

export function assignHazardTicket(
  ticketId: number,
  payload: { owner_id: number; severity?: string; deadline?: string },
): Promise<HazardTicket> {
  return request<HazardTicket>(`/hazard-ticket/${ticketId}/assign`, {
    method: "POST",
    body: payload,
  });
}

export function rectifyHazardTicket(
  ticketId: number,
  rectifyNote: string,
): Promise<HazardTicket> {
  return request<HazardTicket>(`/hazard-ticket/${ticketId}/rectify`, {
    method: "POST",
    body: { rectify_note: rectifyNote },
  });
}

export function reviewHazardTicket(
  ticketId: number,
  approved: boolean,
  rectifyNote?: string,
): Promise<HazardTicket> {
  return request<HazardTicket>(`/hazard-ticket/${ticketId}/review`, {
    method: "POST",
    body: { approved, rectify_note: rectifyNote },
  });
}
