export const NORMAL = "NORMAL";
export const FAULT = "FAULT";
export const MAINTAINING = "MAINTAINING";
export const SCRAPPED = "SCRAPPED";

export const DeviceStatus = [NORMAL, FAULT, MAINTAINING, SCRAPPED] as const;
export type DeviceStatus = (typeof DeviceStatus)[number];

export const DeviceStatusLabels: Record<DeviceStatus, string> = {
  NORMAL: "正常",
  FAULT: "故障",
  MAINTAINING: "整改中",
  SCRAPPED: "停用",
};
