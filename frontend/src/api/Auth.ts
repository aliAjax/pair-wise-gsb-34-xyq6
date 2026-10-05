import { request } from "./client";
import type { LoginResponse } from "../types/User";

export async function login(username: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login", {
    method: "POST",
    body: { username, password },
    raw: true
  });
}
