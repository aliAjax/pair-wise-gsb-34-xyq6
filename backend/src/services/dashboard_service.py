from collections import Counter, defaultdict
from datetime import date

from sqlalchemy.orm import Session

from src.constants.inspection_status import CLOSED_TASK_STATUSES, OVERDUE, PLANNED
from src.constants.rectify_status import CLOSED, OPEN_HAZARD_STATUSES
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository


class DashboardService:
    def __init__(self, db: Session):
        self.device_repo = FireDeviceRepository(db)
        self.ticket_repo = HazardTicketRepository(db)
        self.task_repo = InspectionTaskRepository(db)
        self.result_repo = InspectionResultRepository(db)

    def overview(self) -> dict:
        devices = self.device_repo.find_all()
        tickets = self.ticket_repo.find_all()
        tasks = self.task_repo.find_all()

        device_status = Counter(device.status for device in devices)
        ticket_status = Counter(ticket.rectify_status for ticket in tickets)

        today = date.today().isoformat()
        overdue_tickets = [
            ticket
            for ticket in tickets
            if ticket.rectify_status in OPEN_HAZARD_STATUSES
            and ticket.deadline is not None
            and ticket.deadline.isoformat() < today
        ]
        overdue_tasks = [
            task for task in tasks if task.status == PLANNED and task.plan_date < today
        ]

        finished = [task for task in tasks if task.status in CLOSED_TASK_STATUSES or task.status == OVERDUE]
        completion_rate = round(len(finished) / len(tasks), 4) if tasks else 0

        critical = [
            ticket for ticket in tickets if ticket.severity == "CRITICAL" and ticket.rectify_status != CLOSED
        ]

        return {
            "device_total": len(devices),
            "device_status_distribution": dict(device_status),
            "ticket_status_distribution": dict(ticket_status),
            "open_ticket_count": sum(ticket_status.get(status, 0) for status in OPEN_HAZARD_STATUSES),
            "overdue_ticket_count": len(overdue_tickets),
            "overdue_task_count": len(overdue_tasks),
            "task_total": len(tasks),
            "task_completion_rate": completion_rate,
            "critical_ticket_count": len(critical),
        }

    def monthly_report(self) -> dict:
        tasks = self.task_repo.find_all()
        tickets = self.ticket_repo.list_all()

        task_by_month = Counter((task.plan_date or "")[:7] for task in tasks)
        result_rows = self.result_repo.find_all()
        results_by_task_month = defaultdict(lambda: [0, 0])
        task_month_by_id = {task.id: (task.plan_date or "")[:7] for task in tasks}
        for result in result_rows:
            month = task_month_by_id.get(result.task_id, "未知")
            if result.result_status == "ABNORMAL":
                results_by_task_month[month][1] += 1
            else:
                results_by_task_month[month][0] += 1

        ticket_by_month = Counter(
            (ticket.created_at.date().isoformat() if ticket.created_at else "未知")[:7]
            for ticket in tickets
        )
        closed_ticket_by_month = Counter(
            (ticket.closed_at.date().isoformat() if ticket.closed_at else "")[:7]
            for ticket in tickets
            if ticket.rectify_status == CLOSED and ticket.closed_at
        )

        months = sorted((set(task_by_month) | set(ticket_by_month)) - {""})
        series = []
        for month in months:
            key = month or "未排期"
            normal, abnormal = results_by_task_month.get(month, [0, 0])
            created = ticket_by_month.get(month, 0)
            closed_n = closed_ticket_by_month.get(month, 0)
            rectify_rate = round(closed_n / created, 4) if created else 0
            fault_rate = round(abnormal / (normal + abnormal), 4) if (normal + abnormal) else 0
            series.append({
                "month": key,
                "task_count": task_by_month.get(month, 0),
                "normal_result_count": normal,
                "abnormal_result_count": abnormal,
                "ticket_created": created,
                "ticket_closed": closed_n,
                "rectify_rate": rectify_rate,
                "device_fault_rate": fault_rate,
            })
        return {"months": series}
