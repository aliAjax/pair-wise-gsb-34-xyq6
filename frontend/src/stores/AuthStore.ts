import { create } from "zustand";
import { login as loginApi } from "../api/Auth";
import { getStoredToken, setStoredToken } from "../api/client";
import type { User } from "../types/User";

interface AuthState {
  user: User | null;
  token: string;
  hydrated: boolean;
  hydrate: () => void;
  login: (username: string, password: string) => Promise<User>;
  logout: () => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: "",
  hydrated: false,
  hydrate() {
    const raw = localStorage.getItem("fire-inspect-user");
    const user: User | null = raw ? (JSON.parse(raw) as User) : null;
    set({ user, token: getStoredToken(), hydrated: true });
  },
  async login(username, password) {
    const res = await loginApi(username, password);
    setStoredToken(res.access_token);
    localStorage.setItem("fire-inspect-user", JSON.stringify(res.user));
    set({ user: res.user, token: res.access_token });
    return res.user;
  },
  logout() {
    setStoredToken("");
    localStorage.removeItem("fire-inspect-user");
    set({ user: null, token: "" });
  },
  clearSession() {
    setStoredToken("");
    localStorage.removeItem("fire-inspect-user");
    set({ user: null, token: "" });
  }
}));
