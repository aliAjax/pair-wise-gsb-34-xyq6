import { request } from "./client";
import type { AuthState } from "../types/Auth";
import type { User } from "../types/Auth";

interface LoginResponse extends AuthState {}

export function login(username: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login", { method: "POST", body: { username, password } });
}

export function fetchMe(): Promise<User> {
  return request<User>("/auth/me");
}

export function listUsers(): Promise<User[]> {
  return request<User[]>("/auth/users");
}
