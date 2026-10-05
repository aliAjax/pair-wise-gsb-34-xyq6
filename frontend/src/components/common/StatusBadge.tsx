import { DeviceStatusText } from "../../constants/DeviceStatus";
import { InspectionStatusText } from "../../constants/InspectionStatus";
import { RectifyStatusText } from "../../constants/RectifyStatus";
import { ResultStatusText } from "../../constants/ResultStatus";
import { STATUS_TEXT } from "../../constants/statusText";

const TONE_MAP: Record<string, string> = {
  NORMAL: "ok",
  LIVE: "ok",
  PLANNED: "muted",
  IN_PROGRESS: "progress",
  MAINTAINING: "progress",
  ASSIGNED: "progress",
  OPEN: "danger",
  RECTIFIED: "warn",
  SUBMITTED: "warn",
  ABNORMAL: "danger",
  FAULT: "danger",
  REVIEWED: "ok",
  CLOSED: "ok",
  OVERDUE: "danger",
  SCRAPPED: "muted",
  LOW: "ok",
  MEDIUM: "warn",
  HIGH: "danger",
  CRITICAL: "critical"
};

const TEXT_MAP: Record<string, string> = {
  ...STATUS_TEXT.DeviceType,
  ...DeviceStatusText,
  ...InspectionStatusText,
  ...STATUS_TEXT.HazardSeverity,
  ...ResultStatusText,
  ...RectifyStatusText,
  LIVE: "实时数据"
};

export function StatusBadge({ value, label }: { value: string; label?: string }) {
  const tone = TONE_MAP[value] ?? "muted";
  return (
    <span className={`badge tone-${tone}`} title={value}>
      {label ?? TEXT_MAP[value] ?? value.replace(/_/g, " ")}
    </span>
  );
}
