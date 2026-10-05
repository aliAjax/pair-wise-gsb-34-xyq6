import { useState } from "react";
import { useAuthStore } from "../stores/AuthStore";
import { USER_ROLE_TEXT, type UserRole } from "../types/User";

const DEMO_ACCOUNTS: Array<{ username: string; role: UserRole }> = [
  { username: "inspector_a", role: "INSPECTOR" },
  { username: "inspector_b", role: "INSPECTOR" },
  { username: "maintainer_a", role: "MAINTAINER" },
  { username: "supervisor_a", role: "SUPERVISOR" },
  { username: "auditor_a", role: "AUDITOR" }
];

export function LoginPage() {
  const login = useAuthStore((state) => state.login);
  const [username, setUsername] = useState("inspector_a");
  const [password, setPassword] = useState("inspector_a");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username.trim(), password);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={submit}>
        <p className="eyebrow">fire-inspect</p>
        <h1>消防设施巡检维保平台</h1>
        <label>
          用户名
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          密码
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {error ? <p className="form-error">{error}</p> : null}
        <button className="btn btn-primary" disabled={loading}>
          {loading ? "登录中…" : "登录"}
        </button>
        <div className="demo-accounts">
          <p>演示账号（密码与用户名相同，点击填充）</p>
          <div className="demo-tags">
            {DEMO_ACCOUNTS.map((account) => (
              <button
                type="button"
                key={account.username}
                className="btn btn-ghost"
                onClick={() => {
                  setUsername(account.username);
                  setPassword(account.username);
                }}
              >
                {USER_ROLE_TEXT[account.role]} · {account.username}
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  );
}
