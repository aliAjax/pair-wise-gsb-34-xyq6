"""隐患整改单流转状态。"""

RectifyStatus = ["OPEN", "ASSIGNED", "RECTIFIED", "CLOSED"]

RECTIFY_STATUS_LABELS = {
    "OPEN": "待派单",
    "ASSIGNED": "待整改",
    "RECTIFIED": "待复验",
    "CLOSED": "已关闭",
}
