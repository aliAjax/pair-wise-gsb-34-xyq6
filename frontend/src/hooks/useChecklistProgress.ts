import { useMemo } from "react";
import type { ChecklistItem } from "../types/InspectionTask";

export type ChecklistProgress = {
  total: number;
  filled: number;
  abnormal: number;
  percent: number;
  remaining: string[];
};

// 巡检清单填写进度：供 ChecklistPanel 与提交按钮联动。
export function useChecklistProgress(items: ChecklistItem[] = [], resultMap: Record<string, string> = {}): ChecklistProgress {
  return useMemo(() => {
    const active = items.filter((item) => !item.deprecated);
    const codes = active.map((item) => item.item_code);
    const filledCodes = codes.filter((code) => resultMap[code] !== undefined);
    const abnormal = filledCodes.filter((code) => resultMap[code] === "ABNORMAL").length;
    return {
      total: codes.length,
      filled: filledCodes.length,
      abnormal,
      percent: codes.length ? Math.round((filledCodes.length / codes.length) * 100) : 0,
      remaining: codes.filter((code) => resultMap[code] === undefined),
    };
  }, [items, resultMap]);
}
