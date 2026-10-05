// 角色常量：与 backend/src/constants/roles.py 保持一致。
export const ROLE_INSPECTOR = "INSPECTOR";
export const ROLE_MAINTAINER = "MAINTAINER";
export const ROLE_SUPERVISOR = "SUPERVISOR";
export const ROLE_AUDITOR = "AUDITOR";

export const RoleValues = [ROLE_INSPECTOR, ROLE_MAINTAINER, ROLE_SUPERVISOR, ROLE_AUDITOR] as const;
export type Role = (typeof RoleValues)[number];

export const RoleLabels: Record<Role, string> = {
  INSPECTOR: "巡检员",
  MAINTAINER: "维保人员",
  SUPERVISOR: "物业主管",
  AUDITOR: "审计员",
};

// 演示账号（用户名/密码一致）
export const DEMO_ACCOUNTS: { username: string; role: Role }[] = [
  { username: "inspector", role: ROLE_INSPECTOR },
  { username: "inspector2", role: ROLE_INSPECTOR },
  { username: "maintainer", role: ROLE_MAINTAINER },
  { username: "supervisor", role: ROLE_SUPERVISOR },
  { username: "auditor", role: ROLE_AUDITOR },
];
