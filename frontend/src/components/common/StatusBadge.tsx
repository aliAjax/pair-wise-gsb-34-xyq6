const TONE_MAP: Record<string, string> = {
  NORMAL: "ok",
  PLANNED: "idle",
  REVIEWED: "ok",
  CLOSED: "ok",
  IN_PROGRESS: "progress",
  ASSIGNED: "progress",
  MAINTAINING: "progress",
  RECTIFIED: "progress",
  FAULT: "danger",
  OPEN: "danger",
  REJECTED: "danger",
  OVERDUE: "danger",
  SUBMITTED: "warn",
  SCRAPPED: "muted",
  ABNORMAL: "danger",
};

export function statusTone(value: string): string {
  return TONE_MAP[value] ?? "idle";
}

export function StatusBadge({ value, label }: { value: string; label?: string }) {
  return (
    <span className={`badge tone-${statusTone(value)}`}>
      {label ?? String(value).replace(/_/g, " ")}
    </span>
  );
}
