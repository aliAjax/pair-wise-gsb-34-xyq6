export const OPEN = "OPEN";
export const ASSIGNED = "ASSIGNED";
export const RECTIFIED = "RECTIFIED";
export const CLOSED = "CLOSED";
export const REJECTED = "REJECTED";

export const RectifyStatus = [OPEN, ASSIGNED, RECTIFIED, CLOSED, REJECTED] as const;
export type RectifyStatus = (typeof RectifyStatus)[number];

export const RectifyStatusLabels: Record<RectifyStatus, string> = {
  OPEN: "待派单",
  ASSIGNED: "待整改",
  RECTIFIED: "待复验",
  CLOSED: "已关闭",
  REJECTED: "复验退回",
};
