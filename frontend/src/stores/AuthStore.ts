import { create } from "zustand";
import { fetchMe, login as loginApi } from "../api/Auth";
import { setToken } from "../api/client";
import type { AuthState } from "../types/Auth";

type Store = {
  user: (Omit<AuthState, "token"> & { token?: string }) | null;
  ready: boolean;
  init: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

export const useAuthStore = create<Store>((set) => ({
  user: null,
  ready: false,
  async init() {
    if (!localStorage.getItem("fire-inspect-token")) {
      set({ ready: true });
      return;
    }
    try {
      const me = await fetchMe();
      set({ user: me, ready: true });
    } catch {
      setToken(null);
      set({ user: null, ready: true });
    }
  },
  async login(username, password) {
    const data = await loginApi(username, password);
    setToken(data.token);
    set({ user: { id: data.id, username: data.username, display_name: data.display_name, role: data.role } });
  },
  logout() {
    setToken(null);
    set({ user: null });
  },
}));
