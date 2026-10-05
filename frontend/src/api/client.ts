import { useAuthStore } from "../stores/AuthStore";

const TOKEN_KEY = "fire-inspect-token";

export function getStoredToken(): string {
  return localStorage.getItem(TOKEN_KEY) ?? "";
}

export function setStoredToken(token: string) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  code: string;
  status: number;
  detail?: unknown;

  constructor(code: string, message: string, status: number, detail?: unknown) {
    super(message);
    this.code = code;
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  // 某些请求（如登录）不附带/不触发登录失效处理
  raw?: boolean;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getStoredToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`/api${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined
    });
  } catch {
    throw new ApiError("INTERNAL_ERROR", "网络异常，请稍后再试", 0);
  }

  if (res.status === 204) return undefined as T;
  const payload = await res.json().catch(() => ({}));

  if (!res.ok) {
    const code = payload?.code ?? "INTERNAL_ERROR";
    const message = payload?.message ?? "服务繁忙，请稍后再试";
    if (!options.raw && (code === "AUTH_REQUIRED" || code === "INVALID_TOKEN")) {
      useAuthStore.getState().clearSession();
    }
    throw new ApiError(code, message, res.status, payload?.detail);
  }
  return payload as T;
}
