import { request } from "./client";
import type { HazardTicket } from "../types/HazardTicket";

export interface HazardQuery {
  rectifyStatus?: string;
  severity?: string;
  ownerId?: number;
}

export async function listHazardTicket(query: HazardQuery = {}): Promise<HazardTicket[]> {
  const params = new URLSearchParams();
  if (query.rectifyStatus) params.set("rectify_status", query.rectifyStatus);
  if (query.severity) params.set("severity", query.severity);
  if (query.ownerId) params.set("owner_id", String(query.ownerId));
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return request<HazardTicket[]>(`/hazard-ticket${suffix}`);
}

export async function assignHazardTicket(
  ticketId: number,
  payload: { owner_id: number; deadline?: string; severity?: string }
): Promise<HazardTicket> {
  return request<HazardTicket>(`/hazard-ticket/${ticketId}/assign`, {
    method: "POST",
    body: payload
  });
}

export async function rectifyHazardTicket(
  ticketId: number,
  rectifyNote: string
): Promise<HazardTicket> {
  return request<HazardTicket>(`/hazard-ticket/${ticketId}/rectify`, {
    method: "POST",
    body: { rectify_note: rectifyNote }
  });
}

export async function closeHazardTicket(
  ticketId: number,
  payload: { note: string; pass_review: boolean }
): Promise<HazardTicket> {
  return request<HazardTicket>(`/hazard-ticket/${ticketId}/close`, {
    method: "POST",
    body: payload
  });
}
