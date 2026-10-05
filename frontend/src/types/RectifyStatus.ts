export const RectifyStatus = ["OPEN", "ASSIGNED", "RECTIFIED", "CLOSED"] as const;
export type RectifyStatus = (typeof RectifyStatus)[number];

export const RectifyStatusText: Record<RectifyStatus, string> = {
  OPEN: "待派单",
  ASSIGNED: "待整改",
  RECTIFIED: "待复验",
  CLOSED: "已关闭"
};
