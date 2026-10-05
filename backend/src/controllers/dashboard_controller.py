from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.middlewares.rbac_middleware import current_user
from src.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/overview")
def overview(db: Session = Depends(get_db), user: dict = Depends(current_user)):
    return DashboardService(db).overview()


@router.get("/monthly-report")
def monthly_report(db: Session = Depends(get_db), user: dict = Depends(current_user)):
    return DashboardService(db).monthly_report()
