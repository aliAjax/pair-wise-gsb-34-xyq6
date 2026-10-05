"""消防设备运行状态。"""

DeviceStatus = ["NORMAL", "FAULT", "MAINTAINING", "SCRAPPED"]

DEVICE_STATUS_LABELS = {
    "NORMAL": "正常",
    "FAULT": "故障",
    "MAINTAINING": "整改中",
    "SCRAPPED": "停用",
}
