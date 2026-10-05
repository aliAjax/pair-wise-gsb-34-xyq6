NORMAL = "NORMAL"      # 正常
FAULT = "FAULT"        # 故障/隐患未闭环
MAINTAINING = "MAINTAINING"  # 整改中
SCRAPPED = "SCRAPPED"  # 停用报废

DeviceStatus = [NORMAL, FAULT, MAINTAINING, SCRAPPED]

DEVICE_STATUS_LABELS = {
    NORMAL: "正常",
    FAULT: "故障",
    MAINTAINING: "整改中",
    SCRAPPED: "停用",
}
