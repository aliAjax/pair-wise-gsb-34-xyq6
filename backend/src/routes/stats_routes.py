from fastapi import APIRouter

from src.controllers.stats_controller import dashboard, monthly_report

router = APIRouter(prefix="/api/stats", tags=["Stats"])
router.get("/dashboard", response_model=None)(dashboard)
router.get("/monthly-report", response_model=None)(monthly_report)
