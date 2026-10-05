import { useEffect, useState, type ReactNode } from "react";
import { RoleLabels, type Role } from "../../constants/Role";
import { useAuthStore } from "../../stores/AuthStore";

type RouteDef = {
  name: string;
  route: string;
  roles?: Role[];
  element: ReactNode;
};

export function AppShell({ routes }: { routes: RouteDef[] }) {
  const [active, setActive] = useState<string>(() => window.location.hash.replace(/^#/, "") || routes[0].route);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    const onHash = () => setActive(window.location.hash.replace(/^#/, "") || routes[0].route);
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, [routes]);

  const navigate = (path: string) => {
    window.location.hash = path;
    setActive(path);
  };

  const current = routes.find((route) => route.route === active) ?? routes[0];

  return (
    <div className="shell">
      <aside>
        <div className="brand">消防设施巡检维保平台</div>
        <nav>
          {routes.map((route) => {
            const denied = route.roles && user && !route.roles.includes(user.role);
            return (
              <button
                key={route.route}
                className={active === route.route ? "active" : ""}
                disabled={!!denied}
                title={denied ? "当前角色无权访问该页面" : undefined}
                onClick={() => navigate(route.route)}
              >
                {route.name}
              </button>
            );
          })}
        </nav>
        <div className="aside-user">
          <div className="aside-user-name">{user?.display_name}</div>
          <div className="aside-user-role">{user ? RoleLabels[user.role] : ""}</div>
          <button className="logout-btn" onClick={logout}>退出登录</button>
        </div>
      </aside>
      <div className="content">{current.element}</div>
    </div>
  );
}

export type { RouteDef };
