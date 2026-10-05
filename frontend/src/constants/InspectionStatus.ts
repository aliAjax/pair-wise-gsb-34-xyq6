export const InspectionStatus = ["PLANNED", "IN_PROGRESS", "SUBMITTED", "REVIEWED", "OVERDUE"] as const;
export type InspectionStatus = (typeof InspectionStatus)[number];

export const InspectionStatusText: Record<InspectionStatus, string> = {
  PLANNED: "待领取",
  IN_PROGRESS: "巡检中",
  SUBMITTED: "待复验",
  REVIEWED: "已复验关闭",
  OVERDUE: "已逾期"
};
