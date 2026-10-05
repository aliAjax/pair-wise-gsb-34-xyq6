import { useState } from "react";
import { DEMO_ACCOUNTS, RoleLabels } from "../constants/Role";
import { ApiError } from "../api/client";
import { useAuthStore } from "../stores/AuthStore";

export function LoginPage() {
  const login = useAuthStore((state) => state.login);
  const [username, setUsername] = useState("inspector");
  const [password, setPassword] = useState("inspector");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(username.trim(), password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "登录失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={submit}>
        <p className="eyebrow">fire-inspect</p>
        <h1>消防设施巡检维保平台</h1>
        <p className="muted">请使用巡检员 / 维保人员 / 主管 / 审计员账号登录</p>
        <label>
          用户名
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        </label>
        <label>
          密码
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
        </label>
        {error && <div className="alert alert-danger">{error}</div>}
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "登录中…" : "登录"}
        </button>
        <div className="demo-accounts">
          <p>演示账号（用户名即密码，点击填充）：</p>
          <div className="demo-chips">
            {DEMO_ACCOUNTS.map((account) => (
              <button
                type="button"
                key={account.username}
                className="chip"
                onClick={() => {
                  setUsername(account.username);
                  setPassword(account.username);
                }}
              >
                {RoleLabels[account.role]} · {account.username}
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  );
}
