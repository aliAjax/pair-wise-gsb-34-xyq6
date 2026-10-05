import type { UserRole } from "../types/User";

export interface AppRoute {
  name: string;
  route: string;
  // 空数组表示所有登录角色可见；路由守卫仍可进一步限制动作
  roles: UserRole[];
}

export const routes: AppRoute[] = [
  { name: "消防合规总览", route: "/dashboard", roles: [] },
  { name: "消防设备台账", route: "/devices", roles: [] },
  { name: "巡检任务", route: "/tasks", roles: ["INSPECTOR", "SUPERVISOR"] },
  { name: "隐患整改", route: "/hazards", roles: ["MAINTAINER", "SUPERVISOR"] },
  { name: "合规报表", route: "/reports", roles: ["SUPERVISOR", "AUDITOR"] }
];
