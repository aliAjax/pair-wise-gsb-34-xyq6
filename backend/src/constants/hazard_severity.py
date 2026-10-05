LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"
CRITICAL = "CRITICAL"

HazardSeverity = [LOW, MEDIUM, HIGH, CRITICAL]

HAZARD_SEVERITY_LABELS = {
    LOW: "低危",
    MEDIUM: "中危",
    HIGH: "高危",
    CRITICAL: "严重",
}

# 巡检异常未人工分级时的默认级别。
DEFAULT_SEVERITY = MEDIUM
