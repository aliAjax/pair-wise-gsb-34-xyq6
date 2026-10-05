OPEN = "OPEN"                  # 待派单
ASSIGNED = "ASSIGNED"          # 已派单/待整改
RECTIFIED = "RECTIFIED"        # 已整改/待复验
CLOSED = "CLOSED"              # 复验通过已关闭
REJECTED = "REJECTED"          # 复验不通过，退回整改

RectifyStatus = [OPEN, ASSIGNED, RECTIFIED, CLOSED, REJECTED]

RECTIFY_STATUS_LABELS = {
    OPEN: "待派单",
    ASSIGNED: "待整改",
    RECTIFIED: "待复验",
    CLOSED: "已关闭",
    REJECTED: "复验退回",
}

# 维保人员可以提交整改说明的状态。
MAINTAINABLE_STATUSES = [ASSIGNED, REJECTED]
# 主管可以执行复验关闭/退回的状态。
REVIEWABLE_STATUSES = [RECTIFIED]
# 仍对设备状态造成影响（未闭环）的状态。
OPEN_HAZARD_STATUSES = [OPEN, ASSIGNED, RECTIFIED, REJECTED]
