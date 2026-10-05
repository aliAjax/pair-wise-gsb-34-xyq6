import { DeviceStatusLabels } from "../constants/DeviceStatus";
import { DEVICE_TYPE_LABELS, DeviceTypeTextFallback } from "../constants/deviceLabels";
import { HazardSeverity } from "../constants/HazardSeverity";
import { InspectionStatus } from "../constants/InspectionStatus";
import { RectifyStatusLabels } from "../constants/RectifyStatus";
import { ResultStatusLabels } from "../constants/ResultStatus";

export const formatDate = (value?: string | null) =>
  value ? new Date(value).toLocaleDateString("zh-CN") : "—";

export const formatDateTime = (value?: string | null) =>
  value ? new Date(value).toLocaleString("zh-CN") : "—";

export const formatStatus = (value: string) => value.replace(/_/g, " ");

export const formatNumber = (value: number) => new Intl.NumberFormat("zh-CN").format(value);

export const formatPercent = (value: number) => `${Math.round(value * 100)}%`;

export const formatRisk = (value: string) =>
  ({ LOW: "低危", MEDIUM: "中危", HIGH: "高危", CRITICAL: "严重", EXTREME: "极高" }[value] ?? value);

// 各枚举的统一中文文案出口（筛选器、详情、状态徽标共用）。
export const formatDeviceType = (value: string) =>
  DEVICE_TYPE_LABELS[value] ?? DeviceTypeTextFallback[value] ?? value;

export const formatDeviceStatus = (value: string) => DeviceStatusLabels[value as keyof typeof DeviceStatusLabels] ?? value;

export const formatInspectionStatus = (value: string) =>
  ({
    PLANNED: "待领取",
    IN_PROGRESS: "巡检中",
    SUBMITTED: "待复验",
    REVIEWED: "已复核",
    OVERDUE: "已逾期",
  })[value] ?? value;

export const formatResultStatus = (value: string) =>
  ResultStatusLabels[value as keyof typeof ResultStatusLabels] ?? value;

export const formatRectifyStatus = (value: string) =>
  RectifyStatusLabels[value as keyof typeof RectifyStatusLabels] ?? value;

export const formatSeverity = formatRisk;

export const INSPECTION_STATUS_OPTIONS = InspectionStatus.map((value) => ({ value, label: formatInspectionStatus(value) }));
export const HAZARD_SEVERITY_OPTIONS = HazardSeverity.map((value) => ({ value, label: formatRisk(value) }));
