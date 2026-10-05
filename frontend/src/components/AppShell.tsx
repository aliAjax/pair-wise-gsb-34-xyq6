import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useAuthStore } from "../stores/AuthStore";
import { routes } from "../router/routes";
import { USER_ROLE_TEXT } from "../types/User";

interface AppShellProps {
  active: string;
  onNavigate: (route: string) => void;
  children: ReactNode;
}

export function AppShell({ active, onNavigate, children }: AppShellProps) {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const visibleRoutes = useMemo(
    () =>
      routes.filter(
        (route) => route.roles.length === 0 || (user && route.roles.includes(user.role))
      ),
    [user]
  );

  const current = routes.find((route) => route.route === active);
  const [allowed, setAllowed] = useState(true);
  useEffect(() => {
    if (!current) return;
    setAllowed(current.roles.length === 0 || !!user && current.roles.includes(user.role));
  }, [current, user]);

  return (
    <div className="shell">
      <aside>
        <div className="brand">消防设施巡检维保平台</div>
        <nav>
          {visibleRoutes.map((route) => (
            <button
              key={route.route}
              className={active === route.route ? "active" : ""}
              onClick={() => onNavigate(route.route)}
            >
              {route.name}
            </button>
          ))}
        </nav>
        {user ? (
          <div className="user-box">
            <div>
              <strong>{user.name}</strong>
              <span>{USER_ROLE_TEXT[user.role]}</span>
            </div>
            <button className="btn btn-ghost btn-small" onClick={logout}>
              退出登录
            </button>
          </div>
        ) : null}
      </aside>
      {allowed ? children : <main className="page"><p className="form-error">当前角色无权访问该页面</p></main>}
    </div>
  );
}
