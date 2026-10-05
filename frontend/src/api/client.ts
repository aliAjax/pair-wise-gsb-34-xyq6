// 统一请求封装：所有接口走相对路径 /api，由 Nginx 反代到后端。
import { ERROR_CODES } from "../constants/errorCodes";
import { ERROR_MESSAGES } from "../constants/errorMessages";

const TOKEN_KEY = "fire-inspect-token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | undefined>;
};

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const query = options.query
    ? "?" + new URLSearchParams(
        Object.entries(options.query)
          .filter(([, value]) => value !== undefined && value !== "")
          .map(([key, value]) => [key, String(value)]),
      ).toString()
    : "";
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (options.body !== undefined) headers["Content-Type"] = "application/json";

  let res: Response;
  try {
    res = await fetch(`/api${path}${query}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiError("NETWORK_ERROR", "无法连接后端服务，请确认服务已启动", 0);
  }

  if (res.status === 401) {
    setToken(null);
  }
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const code = (data?.code as string) ?? ERROR_CODES.VALIDATION_FAILED;
    const message = data?.message ?? ERROR_MESSAGES[code as keyof typeof ERROR_MESSAGES] ?? "请求失败";
    throw new ApiError(code, message, res.status);
  }
  return data as T;
}
