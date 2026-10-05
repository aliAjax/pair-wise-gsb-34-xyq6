export const ERROR_MESSAGES = {
  AUTH_REQUIRED: "请先登录后再继续操作",
  INVALID_TOKEN: "登录凭证无效或已过期，请重新登录",
  RBAC_DENIED: "当前角色没有执行该动作的权限",
  VALIDATION_FAILED: "表单字段缺失或格式错误",
  RATE_LIMITED: "请求过于频繁，请稍后再试",
  TASK_NOT_CLAIMABLE: "该巡检任务已被领取或不可领取",
  TASK_NOT_EDITABLE: "巡检任务当前状态不允许再提交检查项",
  CHECKLIST_VERSION_CONFLICT: "清单版本已过期，请刷新清单后重新提交",
  CONCURRENT_SUBMISSION: "该检查项已由其他巡检员提交，同一任务只保留一份结果",
  TASK_INCOMPLETE: "还有检查项未提交，不能提交复核",
  TASK_NOT_REVIEWABLE: "只有待复验的巡检任务可以复验关闭",
  HAZARD_NOT_ASSIGNABLE: "只有待派单的隐患单可以派单",
  HAZARD_NOT_RECTIFIABLE: "只有已派给你的隐患单可以整改",
  HAZARD_NOT_CLOSABLE: "只有整改完成、待复验的隐患单可以关闭",
  INVALID_CREDENTIALS: "用户名或密码错误",
  INTERNAL_ERROR: "服务繁忙，请稍后再试"
} as const;
