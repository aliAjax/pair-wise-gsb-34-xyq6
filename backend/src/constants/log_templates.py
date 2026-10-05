# 操作日志模板：所有写操作均需记录。字段变更时同步修改调用处。
LOG_TEMPLATES = {
    "Auth": [
        "Auth.login|用户 {user_id} 登录系统",
        "Auth.me|校验用户 {user_id} 的会话",
    ],
    "Building": [
        "Building.create|创建楼栋 {building_id}",
        "Building.update|更新楼栋 {building_id} 字段 {fields}",
        "Building.status|楼栋 {building_id} 责任人变更为 {manager_id}",
        "Building.export|导出楼栋台账 {building_id}",
    ],
    "FireDevice": [
        "FireDevice.create|登记消防设备 {device_id}",
        "FireDevice.update|更新消防设备 {device_id} 字段 {fields}",
        "FireDevice.status|消防设备 {device_id} 状态变更为 {status}",
        "FireDevice.export|导出设备台账 {device_id}",
    ],
    "InspectionTask": [
        "InspectionTask.create|创建巡检任务 {task_id}（楼栋 {building_id}，清单版本 {checklist_version}）",
        "InspectionTask.claim|巡检员 {inspector_id} 领取巡检任务 {task_id}",
        "InspectionTask.submit|巡检任务 {task_id} 提交结果，合格 {normal_count} 项，异常 {abnormal_count} 项",
        "InspectionTask.review|主管复核巡检任务 {task_id}，结论 {approved}",
        "InspectionTask.version|巡检任务 {task_id} 清单版本由 {old_version} 升级为 {new_version}",
    ],
    "InspectionResult": [
        "InspectionResult.submit|任务 {task_id} 设备 {device_id} 检查项 {item_code} 结果为 {result_status}",
        "InspectionResult.stale|任务 {task_id} 检查项 {item_code} 因清单版本过期被拒绝（客户端 {client_version} / 当前 {current_version}）",
        "InspectionResult.duplicate|任务 {task_id} 的重复提交被拦截",
        "InspectionResult.export|导出巡检结果 {result_id}",
    ],
    "HazardTicket": [
        "HazardTicket.create|异常结果 {result_id} 生成隐患单 {ticket_id}（级别 {severity}）",
        "HazardTicket.assign|隐患单 {ticket_id} 派单给维保人员 {owner_id}",
        "HazardTicket.rectify|维保人员 {owner_id} 提交隐患单 {ticket_id} 整改说明",
        "HazardTicket.close|主管复验关闭隐患单 {ticket_id}，设备 {device_id} 恢复正常",
        "HazardTicket.reject|主管复验退回隐患单 {ticket_id} 重新整改",
    ],
    "Checklist": [
        "Checklist.publish|发布 {task_type} 清单新版本 {checklist_version}",
        "Checklist.supersede|巡检任务 {task_id} 被新版本清单标记过期",
    ],
}
