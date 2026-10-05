export const HazardSeverity = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
export type HazardSeverity = (typeof HazardSeverity)[number];

export const HazardSeverityText: Record<HazardSeverity, string> = {
  LOW: "低危",
  MEDIUM: "中危",
  HIGH: "高危",
  CRITICAL: "严重"
};
