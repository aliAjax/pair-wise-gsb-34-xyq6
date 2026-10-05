/**
 * 种子数据说明：
 * 线上数据全部由后端 PostgreSQL（本地开发为 SQLite）提供，启动时由
 * backend/src/seed.py 幂等写入，前端不再使用本地假数据兜底。
 *
 * 演示账号（用户名/密码相同）：
 * inspector_a / inspector_b 巡检员；maintainer_a 维保人员；
 * supervisor_a 物业主管；auditor_a 审计员。
 */

export const DEMO_USERS = [
  { username: "inspector_a", role: "INSPECTOR" },
  { username: "inspector_b", role: "INSPECTOR" },
  { username: "maintainer_a", role: "MAINTAINER" },
  { username: "supervisor_a", role: "SUPERVISOR" },
  { username: "auditor_a", role: "AUDITOR" }
] as const;
