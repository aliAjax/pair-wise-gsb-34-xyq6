import type { RouteDef } from "../components/layout/AppShell";
import { DashboardPage } from "../pages/DashboardPage";
import { DevicesPage } from "../pages/DevicesPage";
import { HazardsPage } from "../pages/HazardsPage";
import { LoginPage } from "../pages/LoginPage";
import { ReportsPage } from "../pages/ReportsPage";
import { TasksPage } from "../pages/TasksPage";
import {
  ROLE_AUDITOR,
  ROLE_INSPECTOR,
  ROLE_MAINTAINER,
  ROLE_SUPERVISOR,
} from "../constants/Role";

// 路由守卫元数据：未声明 roles 的页面登录后均可访问；roles 限定可进入的角色。
export const routes: RouteDef[] = [
  { name: "消防合规总览", route: "/dashboard", element: <DashboardPage /> },
  {
    name: "消防设备台账",
    route: "/devices",
    roles: [ROLE_INSPECTOR, ROLE_SUPERVISOR, ROLE_MAINTAINER, ROLE_AUDITOR],
    element: <DevicesPage />,
  },
  {
    name: "巡检任务",
    route: "/tasks",
    roles: [ROLE_INSPECTOR, ROLE_SUPERVISOR],
    element: <TasksPage />,
  },
  {
    name: "隐患整改",
    route: "/hazards",
    roles: [ROLE_SUPERVISOR, ROLE_MAINTAINER, ROLE_INSPECTOR],
    element: <HazardsPage />,
  },
  {
    name: "合规报表/审计",
    route: "/reports",
    roles: [ROLE_SUPERVISOR, ROLE_AUDITOR],
    element: <ReportsPage />,
  },
];

export { LoginPage };
