import { useMemo } from "react";
import type { HazardTicket } from "../types/HazardTicket";

/**
 * 隐患流转：按 OPEN -> ASSIGNED -> RECTIFIED -> CLOSED 统计各阶段数量与下一步动作权限。
 */
export function useHazardFlow(rows: HazardTicket[] = []) {
  const stages = useMemo(
    () => [
      { key: "OPEN", label: "待派单", count: rows.filter((r) => r.rectify_status === "OPEN").length },
      { key: "ASSIGNED", label: "待整改", count: rows.filter((r) => r.rectify_status === "ASSIGNED").length },
      { key: "RECTIFIED", label: "待复验", count: rows.filter((r) => r.rectify_status === "RECTIFIED").length },
      { key: "CLOSED", label: "已关闭", count: rows.filter((r) => r.rectify_status === "CLOSED").length }
    ],
    [rows]
  );
  const overdueCount = rows.filter((r) => r.overdue).length;
  return { stages, overdueCount };
}
