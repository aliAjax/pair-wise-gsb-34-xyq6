export const DeviceStatus = ["NORMAL", "FAULT", "MAINTAINING", "SCRAPPED"] as const;
export type DeviceStatus = (typeof DeviceStatus)[number];

export const DeviceStatusText: Record<DeviceStatus, string> = {
  NORMAL: "正常",
  FAULT: "故障",
  MAINTAINING: "整改中",
  SCRAPPED: "停用"
};
