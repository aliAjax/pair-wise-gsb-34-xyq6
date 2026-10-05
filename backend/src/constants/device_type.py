DeviceType = ["EXTINGUISHER", "HYDRANT", "SMOKE_DETECTOR", "SPRINKLER", "EXIT_LIGHT"]

DEVICE_TYPE_LABELS = {
    "EXTINGUISHER": "灭火器",
    "HYDRANT": "消火栓",
    "SMOKE_DETECTOR": "烟感探测器",
    "SPRINKLER": "喷淋头",
    "EXIT_LIGHT": "应急疏散灯",
}

# 不同设备类型对应的标准检查项（生成巡检清单时使用）
DEVICE_CHECKLIST = {
    "EXTINGUISHER": [
        ("PRESSURE", "压力表指针是否在绿区"),
        ("WEIGHT", "灭火剂重量是否达标"),
        ("EXPIRY", "是否在有效期内"),
    ],
    "HYDRANT": [
        ("WATER_PRESSURE", "出水压力是否正常"),
        ("VALVE", "阀门启闭是否灵活"),
        ("BOX", "箱体水带枪头是否齐全"),
    ],
    "SMOKE_DETECTOR": [
        ("INDICATOR", "巡检指示灯是否正常"),
        ("TEST", "按测试键是否报警"),
        ("APPEARANCE", "外观与底座是否完好"),
    ],
    "SPRINKLER": [
        ("GLASS_BULB", "玻璃球是否完好"),
        ("LEAK", "有无渗水滴漏"),
        ("DISTANCE", "遮挡物距离是否合规"),
    ],
    "EXIT_LIGHT": [
        ("LAMP", "主电指示灯是否点亮"),
        ("BATTERY", "断电应急能否点亮"),
        ("SIGN", "疏散标识是否清晰"),
    ],
}
