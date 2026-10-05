import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "./components/AppShell";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { TasksPage } from "./pages/TasksPage";
import { HazardsPage } from "./pages/HazardsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { routes } from "./router/routes";
import { useAuthStore } from "./stores/AuthStore";
import "./styles.css";

function App() {
  const user = useAuthStore((state) => state.user);
  const hydrated = useAuthStore((state) => state.hydrated);
  const hydrate = useAuthStore((state) => state.hydrate);
  const [active, setActive] = useState<string>(routes[0]?.route ?? "/dashboard");

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  if (!hydrated) return null;
  if (!user) return <LoginPage />;

  const allowed = routes.find((r) => r.route === active && (r.roles.length === 0 || r.roles.includes(user.role)));
  const pageRoute = allowed ? active : "/dashboard";

  return (
    <AppShell active={pageRoute} onNavigate={setActive}>
      {pageRoute === "/dashboard" && <DashboardPage />}
      {pageRoute === "/devices" && <DevicesPage />}
      {pageRoute === "/tasks" && <TasksPage />}
      {pageRoute === "/hazards" && <HazardsPage />}
      {pageRoute === "/reports" && <ReportsPage />}
    </AppShell>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
