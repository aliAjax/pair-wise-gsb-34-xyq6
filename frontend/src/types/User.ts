export interface User {
  id: number;
  username: string;
  name: string;
  role: UserRole;
}

export const USER_ROLES = ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"] as const;
export type UserRole = (typeof USER_ROLES)[number];

export const USER_ROLE_TEXT: Record<UserRole, string> = {
  INSPECTOR: "巡检员",
  MAINTAINER: "维保人员",
  SUPERVISOR: "物业主管",
  AUDITOR: "审计员"
};

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
