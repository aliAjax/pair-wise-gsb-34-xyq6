import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { AppShell } from "./components/layout/AppShell";
import { LoginPage } from "./pages/LoginPage";
import { routes } from "./router/routes";
import { useAuthStore } from "./stores/AuthStore";

function App() {
  const user = useAuthStore((state) => state.user);
  const ready = useAuthStore((state) => state.ready);
  const init = useAuthStore((state) => state.init);
  const [booted, setBooted] = useState(false);

  useEffect(() => {
    init().finally(() => setBooted(true));
  }, [init]);

  if (!ready || !booted) {
    return <div className="booting">正在加载消防巡检数据…</div>;
  }
  if (!user) return <LoginPage />;
  return <AppShell routes={routes} />;
}

createRoot(document.getElementById("root")!).render(<App />);
