import { useMemo } from "react";
import type { ChecklistItem } from "../types/InspectionTask";

/**
 * 巡检清单进度：已提交数 / 总数 / 异常数 / 完成率。
 */
export function useChecklistProgress(items: ChecklistItem[] = []) {
  return useMemo(() => {
    const total = items.length;
    const submitted = items.filter((item) => item.result_status !== null).length;
    const abnormal = items.filter((item) => item.result_status === "ABNORMAL").length;
    const normal = submitted - abnormal;
    const percent = total === 0 ? 0 : Math.round((submitted / total) * 100);
    return { total, submitted, abnormal, normal, percent, remaining: total - submitted };
  }, [items]);
}
