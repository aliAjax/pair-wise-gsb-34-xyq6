import { formatRisk } from "../../utils/formatters";

const TONE: Record<string, string> = {
  LOW: "tone-idle",
  MEDIUM: "tone-warn",
  HIGH: "tone-danger",
  CRITICAL: "tone-danger",
};

export function HazardSeverityTag({ value }: { value: string }) {
  return <span className={`badge ${TONE[value] ?? "tone-idle"}`}>{formatRisk(value)}</span>;
}
