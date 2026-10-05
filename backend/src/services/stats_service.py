"""总览统计与月度合规报表：全部基于设备状态、任务与隐患单实时重算。"""

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.constructors.stats_factory import create_dashboard_stats, create_monthly_report_row
from src.models.entities import FireDevice, HazardTicket, InspectionResult, InspectionTask, utcnow


class StatsService:
    def __init__(self, session: Session):
        self.session = session

    def dashboard(self) -> dict:
        devices = list(self.session.scalars(select(FireDevice)))
        tasks = list(self.session.scalars(select(InspectionTask)))
        tickets = list(self.session.scalars(select(HazardTicket)))
        now = utcnow()

        open_tickets = [t for t in tickets if t.rectify_status != "CLOSED"]
        overdue = [t for t in open_tickets if t.deadline is not None and t.deadline < now]
        critical = [t for t in open_tickets if t.severity == "CRITICAL"]
        finished_tasks = [t for t in tasks if t.status in ("SUBMITTED", "REVIEWED")]

        rate = lambda done, total: round(done / total, 4) if total else 0.0
        return create_dashboard_stats(
            device_total=len(devices),
            device_normal=sum(1 for d in devices if d.status == "NORMAL"),
            device_fault=sum(1 for d in devices if d.status == "FAULT"),
            device_maintaining=sum(1 for d in devices if d.status == "MAINTAINING"),
            device_scrapped=sum(1 for d in devices if d.status == "SCRAPPED"),
            open_hazard_total=len(open_tickets),
            overdue_hazard_total=len(overdue),
            critical_hazard_total=len(critical),
            task_total=len(tasks),
            task_finished=len(finished_tasks),
            inspection_completion_rate=rate(len(finished_tasks), len(tasks)),
            rectification_rate=rate(
                sum(1 for t in tickets if t.rectify_status == "CLOSED"), len(tickets)
            ),
        )

    def monthly_report(self) -> list[dict]:
        tasks = list(self.session.scalars(select(InspectionTask)))
        tickets = list(self.session.scalars(select(HazardTicket)))
        results = list(self.session.scalars(select(InspectionResult)))

        months = sorted(
            {
                *(t.plan_date.strftime("%Y-%m") for t in tasks if t.plan_date),
                *(t.created_at.strftime("%Y-%m") for t in tickets if t.created_at),
            }
        )
        task_by_month: dict[str, list[InspectionTask]] = defaultdict(list)
        for task in tasks:
            if task.plan_date:
                task_by_month[task.plan_date.strftime("%Y-%m")].append(task)

        ticket_by_month: dict[str, list[HazardTicket]] = defaultdict(list)
        for ticket in tickets:
            if ticket.created_at:
                ticket_by_month[ticket.created_at.strftime("%Y-%m")].append(ticket)

        abnormal_device_sets: dict[str, set[int]] = defaultdict(set)
        task_plan_by_id = {t.id: t.plan_date for t in tasks}
        for result in results:
            if result.result_status == "ABNORMAL":
                plan = task_plan_by_id.get(result.task_id)
                if plan:
                    abnormal_device_sets[plan.strftime("%Y-%m")].add(result.device_id)

        rate = lambda done, total: round(done / total, 4) if total else 0.0
        rows = []
        for month in months:
            month_tasks = task_by_month.get(month, [])
            month_tickets = ticket_by_month.get(month, [])
            finished = [t for t in month_tasks if t.status in ("SUBMITTED", "REVIEWED")]
            closed = [t for t in month_tickets if t.rectify_status == "CLOSED"]
            rows.append(
                create_monthly_report_row(
                    month,
                    task_total=len(month_tasks),
                    task_finished=len(finished),
                    inspection_rate=rate(len(finished), len(month_tasks)),
                    hazard_total=len(month_tickets),
                    hazard_closed=len(closed),
                    rectification_rate=rate(len(closed), len(month_tickets)),
                    abnormal_device_count=len(abnormal_device_sets.get(month, set())),
                )
            )
        return rows
