"""总览/报表统计 DTO 构造器。"""


def create_dashboard_stats(**values) -> dict:
    return {
        "device_total": 0,
        "device_normal": 0,
        "device_fault": 0,
        "device_maintaining": 0,
        "device_scrapped": 0,
        "open_hazard_total": 0,
        "overdue_hazard_total": 0,
        "critical_hazard_total": 0,
        "task_total": 0,
        "task_finished": 0,
        "inspection_completion_rate": 0.0,
        "rectification_rate": 0.0,
        **values,
    }


def create_monthly_report_row(month: str, **values) -> dict:
    return {
        "month": month,
        "task_total": 0,
        "task_finished": 0,
        "inspection_rate": 0.0,
        "hazard_total": 0,
        "hazard_closed": 0,
        "rectification_rate": 0.0,
        "abnormal_device_count": 0,
        **values,
    }
