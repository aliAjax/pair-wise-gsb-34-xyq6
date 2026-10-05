import { DeviceStatusText } from "../constants/DeviceStatus";
import { DeviceTypeText } from "../constants/DeviceType";
import { HazardSeverityText } from "../constants/HazardSeverity";
import { InspectionStatusText } from "../constants/InspectionStatus";
import { RectifyStatusText } from "../constants/RectifyStatus";
import { ResultStatusText } from "../constants/ResultStatus";
import { USER_ROLE_TEXT, type UserRole } from "../types/User";

export const formatDate = (value?: string | null) =>
  value ? new Date(value).toLocaleString("zh-CN") : "—";

export const formatDay = (value?: string | null) =>
  value ? new Date(value).toLocaleDateString("zh-CN") : "—";

export const formatStatus = (value: string) => value.replace(/_/g, " ");

export const formatNumber = (value: number) => new Intl.NumberFormat("zh-CN").format(value);

export const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

export const formatRisk = (value: string) =>
  HazardSeverityText[value as keyof typeof HazardSeverityText] ?? value;

export const formatDeviceType = (value: string) =>
  DeviceTypeText[value as keyof typeof DeviceTypeText] ?? value;

export const formatDeviceStatus = (value: string) =>
  DeviceStatusText[value as keyof typeof DeviceStatusText] ?? value;

export const formatInspectionStatus = (value: string) =>
  InspectionStatusText[value as keyof typeof InspectionStatusText] ?? value;

export const formatResultStatus = (value: string) =>
  ResultStatusText[value as keyof typeof ResultStatusText] ?? value;

export const formatRectifyStatus = (value: string) =>
  RectifyStatusText[value as keyof typeof RectifyStatusText] ?? value;

export const formatRole = (value: string) => USER_ROLE_TEXT[value as UserRole] ?? value;
