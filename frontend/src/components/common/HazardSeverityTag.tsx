import { HazardSeverityText } from "../../constants/HazardSeverity";
import { StatusBadge } from "./StatusBadge";

export function HazardSeverityTag({ value }: { value: string }) {
  return (
    <StatusBadge
      value={value}
      label={HazardSeverityText[value as keyof typeof HazardSeverityText] ?? value}
    />
  );
}
